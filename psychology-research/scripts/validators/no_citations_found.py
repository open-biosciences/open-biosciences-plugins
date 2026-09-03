"""No-citations-found validator (WARN).

Three content validators — citation, evidence_label_coverage, source_tier_minimum
— only inspect sentences containing an inline ``[S\\d+]`` marker, and
bibliography_integrity compares two sets that are both empty when no markers
exist. A report that carries its sources in some other shape (e.g. inline
markdown links inside a claim table) therefore passes all four *without being
examined*: the gate fails open.

This validator closes that hole. It does not judge the citation style; it only
asserts that the gate found something to check.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.validators import Severity, ValidatorResult

_CITATION_RE = re.compile(r"\[S\d+\]")

# A report that cites nothing at all is a different (legitimate) case from one
# that cites in an unrecognised shape. Look for any link or bare URL as evidence
# that sourcing was attempted.
_ANY_SOURCE_RE = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)|https?://\S+")


def validate_no_citations_found(report_path: Path) -> ValidatorResult:
    text = report_path.read_text(encoding="utf-8")

    if _CITATION_RE.search(text):
        return ValidatorResult(
            name="no_citations_found", severity=Severity.PASS, findings=[]
        )

    findings = [
        "no [Sn] citation markers found; the citation, evidence-label-coverage, "
        "source-tier-minimum and bibliography-integrity validators had nothing "
        "to inspect and their PASS results are vacuous."
    ]
    if _ANY_SOURCE_RE.search(text):
        findings.append(
            "the report does contain links or URLs, so sources are present in a "
            "shape the gate does not recognise. Render sources as "
            "'- [S1] Title - Publisher - url - retrieved YYYY-MM-DD' under a "
            "'## Sources' heading and mark body claims with [Sn]."
        )

    return ValidatorResult(
        name="no_citations_found", severity=Severity.WARN, findings=findings
    )
