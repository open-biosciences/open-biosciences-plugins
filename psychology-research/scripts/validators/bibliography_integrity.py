"""Bibliography-integrity validator (BLOCK).

Every body marker [S\\d+] has a corresponding entry in the bibliography section;
every entry is referenced at least once.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.validators import Severity, ValidatorResult


_MARKER_RE = re.compile(r"\[S(\d+)\]")
_SOURCES_HEADING_RE = re.compile(r"^\s*##\s*Sources\s*$", re.IGNORECASE | re.MULTILINE)
_SOURCE_LINE_RE = re.compile(r"^\s*-\s*\[S(\d+)\]", re.MULTILINE)


def validate_bibliography_integrity(report_path: Path) -> ValidatorResult:
    text = report_path.read_text(encoding="utf-8")
    heading_match = _SOURCES_HEADING_RE.search(text)
    body = text if not heading_match else text[: heading_match.start()]
    biblio = "" if not heading_match else text[heading_match.end():]

    body_ids = {f"S{m}" for m in _MARKER_RE.findall(body)}
    biblio_ids = {f"S{m}" for m in _SOURCE_LINE_RE.findall(biblio)}

    findings: list[str] = []
    for sid in sorted(body_ids - biblio_ids):
        findings.append(f"orphan body marker (no bibliography entry): {sid}")
    for sid in sorted(biblio_ids - body_ids):
        findings.append(f"unreferenced bibliography entry: {sid}")

    severity = Severity.BLOCK if findings else Severity.PASS
    return ValidatorResult(
        name="bibliography_integrity",
        severity=severity,
        findings=findings,
    )
