"""Crisis-trigger validator (BLOCK).

If the report contains crisis keywords, the synced-in crisis-resources.md content
must appear byte-for-byte unmodified somewhere in the report.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.validators import Severity, ValidatorResult


_CRISIS_KEYWORDS = re.compile(
    r"\b(suicide|suicidal|self[- ]harm|self[- ]injury|abuse(?:r|d|s|ing)?|"
    r"crisis|psychiatric emergency|imminent danger|safety plan)\b",
    re.IGNORECASE,
)


def validate_crisis_trigger(report_path: Path, crisis_ref_path: Path) -> ValidatorResult:
    text = report_path.read_text(encoding="utf-8")
    has_keyword = bool(_CRISIS_KEYWORDS.search(text))
    if not has_keyword:
        return ValidatorResult(name="crisis_trigger", severity=Severity.PASS, findings=[])

    preamble = crisis_ref_path.read_text(encoding="utf-8").strip()
    # Require the full preamble text to appear unmodified somewhere in the report.
    if preamble in text:
        return ValidatorResult(name="crisis_trigger", severity=Severity.PASS, findings=[])

    return ValidatorResult(
        name="crisis_trigger",
        severity=Severity.BLOCK,
        findings=[
            "report contains crisis keywords but the crisis-resources preamble "
            "is not present byte-for-byte; the safety preamble must be included "
            "verbatim from references/crisis-resources.md."
        ],
    )


def make_registry_entry(crisis_ref_path: Path):
    def _runner(report_path: Path) -> ValidatorResult:
        return validate_crisis_trigger(report_path, crisis_ref_path)
    _runner.__name__ = "crisis_trigger"
    return _runner
