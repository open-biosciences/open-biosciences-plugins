"""Template-conformance validator (BLOCK).

Required report sections must be present in canonical order:
  Answer, Evidence Packet Summary, Local Context vs External Evidence, Gaps, Sources.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.validators import Severity, ValidatorResult


_REQUIRED = [
    "Answer",
    "Evidence Packet Summary",
    "Local Context vs External Evidence",
    "Gaps",
    "Sources",
]


def validate_template_conformance(report_path: Path) -> ValidatorResult:
    text = report_path.read_text(encoding="utf-8")
    findings: list[str] = []

    positions: list[int] = []
    for name in _REQUIRED:
        m = re.search(r"^\s*##\s*" + re.escape(name) + r"\s*$",
                      text, re.IGNORECASE | re.MULTILINE)
        if not m:
            findings.append(f"missing required section: ## {name}")
            positions.append(-1)
        else:
            positions.append(m.start())

    if all(p >= 0 for p in positions):
        # Check canonical order.
        for i in range(len(positions) - 1):
            if positions[i] > positions[i + 1]:
                findings.append(
                    f"sections out of canonical order: "
                    f"'{_REQUIRED[i]}' appears after '{_REQUIRED[i + 1]}'"
                )

    severity = Severity.BLOCK if findings else Severity.PASS
    return ValidatorResult(
        name="template_conformance",
        severity=severity,
        findings=findings,
    )
