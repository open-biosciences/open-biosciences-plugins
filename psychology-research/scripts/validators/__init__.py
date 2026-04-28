"""Validator registry. Tier-1a populates with seven validators."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Severity(Enum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class ValidatorResult:
    name: str
    severity: Severity
    findings: list[str]


# Each registered validator is a callable: (report_path: Path) -> ValidatorResult
# Populated as Tasks 11-17 land.
REGISTRY: list = []
