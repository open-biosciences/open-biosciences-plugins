"""Citation validator (BLOCK).

Citation-side structural floor: every citation must hit a baseline source-quality
floor regardless of claim severity. Tier 6 patterns from source-tiers.yaml are
structurally rejected (Scribd, generic unattributed PDFs, etc.).
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.source_tiers_loader import load_tiers, lookup_tier
from scripts.validators import Severity, ValidatorResult


_URL_RE = re.compile(r"https?://[^\s)\]]+")


def validate_citations(report_path: Path, tiers_path: Path) -> ValidatorResult:
    tiers = load_tiers(tiers_path)
    text = report_path.read_text(encoding="utf-8")
    findings: list[str] = []

    for url in _URL_RE.findall(text):
        tier = lookup_tier(url, tiers)
        if tier is not None and tier >= 6:
            findings.append(f"structurally rejected source (tier {tier}): {url}")

    severity = Severity.BLOCK if findings else Severity.PASS
    return ValidatorResult(
        name="citation",
        severity=severity,
        findings=findings,
    )


# Module-level callable for the registry: closure over the canonical tiers path.
def make_registry_entry(tiers_path: Path):
    def _runner(report_path: Path) -> ValidatorResult:
        return validate_citations(report_path, tiers_path)
    _runner.__name__ = "citation"
    return _runner
