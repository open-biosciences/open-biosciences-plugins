"""Source-tier-minimum validator (WARN).

Claim-side judgment: high-stakes claims should cite tier 1/2 sources. Tier-1a
heuristic: a sentence is high-stakes if it contains any high-stakes keyword AND
contains an inline citation marker. If the citation resolves to tier > 2, WARN.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.source_tiers_loader import load_tiers, lookup_tier
from scripts.validators import Severity, ValidatorResult


_HIGH_STAKES_TERMS = re.compile(
    r"\b(licensed|certified|certification|evidence[- ]based|effective|"
    r"efficacy|treatment|diagnosis|clinical|board[- ]certified)\b",
    re.IGNORECASE,
)
_CITATION_RE = re.compile(r"\[S(\d+)\]")
_SOURCE_LINE_RE = re.compile(r"^\s*-\s*\[S(\d+)\]\s+(.*)$")
_URL_RE = re.compile(r"https?://[^\s)\]]+")


def _build_source_map(text: str) -> dict[str, str]:
    """Map source ID (e.g., 'S1') -> first URL found in its source line."""
    src: dict[str, str] = {}
    for line in text.splitlines():
        m = _SOURCE_LINE_RE.match(line)
        if not m:
            continue
        url_match = _URL_RE.search(m.group(2))
        if url_match:
            src[f"S{m.group(1)}"] = url_match.group(0)
    return src


def validate_source_tier_minimum(report_path: Path, tiers_path: Path) -> ValidatorResult:
    tiers = load_tiers(tiers_path)
    text = report_path.read_text(encoding="utf-8")
    sources = _build_source_map(text)
    findings: list[str] = []

    # Split on blank lines to get paragraphs, then on sentence boundaries within
    # each paragraph. A citation [Sx] trailing after a period is kept with the
    # preceding sentence by joining split fragments that start with a citation.
    paragraphs = re.split(r"\n{2,}", text)
    raw_sentences: list[str] = []
    for para in paragraphs:
        parts = re.split(r"(?<=[.!?]) +", para)
        # Re-join fragments that start with a bare citation (e.g. "[S1] ...")
        # so the citation stays with the preceding sentence.
        joined: list[str] = []
        for part in parts:
            if joined and re.match(r"^\[S\d+\]", part.strip()):
                joined[-1] = joined[-1] + " " + part
            else:
                joined.append(part)
        raw_sentences.extend(joined)

    for sentence in raw_sentences:
        if not _HIGH_STAKES_TERMS.search(sentence):
            continue
        ids = _CITATION_RE.findall(sentence)
        if not ids:
            continue
        # Best tier across cited sources.
        best: int | None = None
        for sid in ids:
            url = sources.get(f"S{sid}")
            if not url:
                continue
            tier = lookup_tier(url, tiers)
            if tier is None:
                continue
            best = tier if best is None else min(best, tier)
        if best is not None and best > 2:
            findings.append(
                f"high-stakes claim cites only tier-{best} source(s): "
                f"{sentence.strip()[:120]}"
            )

    severity = Severity.WARN if findings else Severity.PASS
    return ValidatorResult(
        name="source_tier_minimum",
        severity=severity,
        findings=findings,
    )


def make_registry_entry(tiers_path: Path):
    def _runner(report_path: Path) -> ValidatorResult:
        return validate_source_tier_minimum(report_path, tiers_path)
    _runner.__name__ = "source_tier_minimum"
    return _runner
