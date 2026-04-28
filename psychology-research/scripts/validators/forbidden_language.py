"""Forbidden-language validator (WARN).

Lexical scan against references/forbidden-language.md. Word-boundary, case-insensitive.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.validators import Severity, ValidatorResult


_BULLET_RE = re.compile(r"^\s*-\s+(.+?)\s*$")


def load_wordlist(path: Path) -> list[str]:
    """Extract bullet-list terms from forbidden-language.md.

    Headings and paragraphs are ignored; only `- term` lines are picked up.
    Bullets under the `## Note` heading are excluded.
    """
    terms: list[str] = []
    in_note = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("## Note"):
            in_note = True
            continue
        if line.startswith("##"):
            in_note = False
            continue
        if in_note:
            continue
        m = _BULLET_RE.match(line)
        if m:
            terms.append(m.group(1).strip())
    return terms


def validate_forbidden_language(report_path: Path, wordlist_path: Path) -> ValidatorResult:
    terms = load_wordlist(wordlist_path)
    text = report_path.read_text(encoding="utf-8")
    findings: list[str] = []

    for term in terms:
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            findings.append(f"'{term}' at ...{text[start:end].strip()}...")

    severity = Severity.WARN if findings else Severity.PASS
    return ValidatorResult(
        name="forbidden_language",
        severity=severity,
        findings=findings,
    )


def make_registry_entry(wordlist_path: Path):
    def _runner(report_path: Path) -> ValidatorResult:
        return validate_forbidden_language(report_path, wordlist_path)
    _runner.__name__ = "forbidden_language"
    return _runner
