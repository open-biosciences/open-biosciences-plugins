"""Template-conformance validator (BLOCK).

Required report sections must be present in canonical order:
  Answer, Evidence Packet Summary, Local Context vs External Evidence, Gaps, Sources.

The report's status lines are checked here too, because they are part of the
report's shape rather than its evidence:

* The unvalidated-draft watermark must be present and must be the final line.
* No retired provenance banner may appear. A banner that asserts a capability
  the plugin no longer lacks understates the report's own provenance; see
  RETIRED_BANNERS for the history of each entry.
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

# Substring that identifies the unvalidated-draft watermark footer. Matched on
# the marker rather than the full sentence so that wording may be revised
# without silently disabling the check.
WATERMARK_MARKER = "STATUS: UNVALIDATED DRAFT"

# Provenance banners that were true once and are false now. Each entry is
# matched as a substring; keep the distinctive clause, not the whole sentence.
#
#   "literature MCP not yet wired"
#       Tier-1a banner, introduced 2026-04-28 (commit 52f5b17) when no
#       literature MCP was bound. Falsified 2026-08-15 (commit 2dfb829,
#       AGE-587) when `psychology-mcp` was declared in `.mcp.json`.
RETIRED_BANNERS = [
    "literature MCP not yet wired",
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

    findings.extend(_check_status_lines(text))

    severity = Severity.BLOCK if findings else Severity.PASS
    return ValidatorResult(
        name="template_conformance",
        severity=severity,
        findings=findings,
    )


def _check_status_lines(text: str) -> list[str]:
    """Check the watermark footer and guard against retired banners."""
    findings: list[str] = []

    for banner in RETIRED_BANNERS:
        if banner in text:
            findings.append(
                f"retired provenance banner present: {banner!r}. This banner "
                "was accurate in an earlier plugin version and is false now; "
                "remove it rather than re-emitting it."
            )

    if WATERMARK_MARKER not in text:
        findings.append(
            f"missing unvalidated-draft watermark footer ({WATERMARK_MARKER!r}). "
            "A report that has not passed the publish gate must say so."
        )
        return findings

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if lines and WATERMARK_MARKER not in lines[-1]:
        findings.append(
            "unvalidated-draft watermark is not the final line of the report; "
            "a footer a reader scrolls past does not warn anyone."
        )

    return findings
