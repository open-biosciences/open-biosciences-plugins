"""Evidence-label-coverage validator (BLOCK).

Tier-1a heuristic: every sentence that contains an inline citation [S\\d+] and
is outside the Limits/Gaps/Sources sections must contain one of the evidence
label keywords (VERIFIED, SELF_REPORTED, SUPPORTED, UNRESOLVED, CONFLICTING) or
the (local synthesis) annotation.

Refining the claim-sentence heuristic is a Tier-N concern.

Implementation note: citation markers such as ``[S1]`` often appear *after* the
sentence terminator on the same logical line, e.g.::

    AEDP is the gold standard. [S1]

The naive ``[^.!?\\n]+[.!?]`` fragment only captures the part up to the period,
so ``[S1]`` would be invisible.  We fix this by extending each sentence fragment
to include any ``[Sx]`` tokens that immediately follow the terminator on the
same line (before the next ``\\n``).  This is the same class of fix applied in
the Task 12 / source-tier-minimum work.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.validators import Severity, ValidatorResult


_LABEL_RE = re.compile(
    r"\b(VERIFIED|SELF[_ ]REPORTED|SUPPORTED|UNRESOLVED|CONFLICTING)\b"
)
_LOCAL_SYNTHESIS_RE = re.compile(r"\(local synthesis\)", re.IGNORECASE)
_CITATION_RE = re.compile(r"\[S\d+\]")
_EXEMPT_SECTIONS = {"gaps", "limits", "sources"}

# Matches a sentence-shaped fragment: one or more non-terminator, non-newline
# chars followed by a sentence terminator.
_SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]")

# Matches one or more citation tokens (with optional surrounding whitespace)
# that appear on the remainder of the same line after a sentence terminator.
_TRAILING_CITATIONS_RE = re.compile(r"(?:[ \t]*\[S\d+\])+")


def _section_at(text: str, idx: int) -> str:
    """Return the lowercased title of the most recent heading before *idx*."""
    head = text[:idx]
    matches = list(re.finditer(r"^\s*#+\s*(.+?)\s*$", head, re.MULTILINE))
    if not matches:
        return ""
    return matches[-1].group(1).lower().strip()


def validate_evidence_label_coverage(report_path: Path) -> ValidatorResult:
    text = report_path.read_text(encoding="utf-8")
    findings: list[str] = []

    for sentence_match in _SENTENCE_RE.finditer(text):
        sentence = sentence_match.group(0)
        end = sentence_match.end()

        # Extend the fragment to absorb any trailing [Sx] markers on the same
        # line (before the next newline).  This handles the common pattern:
        #   "Claim text. [S1]"
        # where [S1] follows the period.
        trailing = _TRAILING_CITATIONS_RE.match(text, end)
        if trailing:
            sentence = sentence + trailing.group(0)

        if not _CITATION_RE.search(sentence):
            continue

        section = _section_at(text, sentence_match.start())
        if any(section.startswith(s) for s in _EXEMPT_SECTIONS):
            continue

        if _LABEL_RE.search(sentence) or _LOCAL_SYNTHESIS_RE.search(sentence):
            continue

        findings.append(f"unlabeled claim: {sentence.strip()[:120]}")

    severity = Severity.BLOCK if findings else Severity.PASS
    return ValidatorResult(
        name="evidence_label_coverage",
        severity=severity,
        findings=findings,
    )
