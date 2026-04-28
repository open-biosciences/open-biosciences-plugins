"""Validator registry. Tier-1a registers seven validators with locked severities."""

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


# Resolved relative to the repository root psychology-research/.
_PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
_REFS = _PLUGIN_ROOT / "references"

REGISTRY: list = []


def populate_registry() -> None:
    """Populate REGISTRY with the Tier-1a seven validators."""
    REGISTRY.clear()

    # Imports here to avoid circular imports at module load.
    from scripts.validators.citation import make_registry_entry as citation_entry
    from scripts.validators.source_tier_minimum import make_registry_entry as stm_entry
    from scripts.validators.forbidden_language import make_registry_entry as fl_entry
    from scripts.validators.crisis_trigger import make_registry_entry as ct_entry
    from scripts.validators.evidence_label_coverage import (
        validate_evidence_label_coverage,
    )
    from scripts.validators.bibliography_integrity import (
        validate_bibliography_integrity,
    )
    from scripts.validators.template_conformance import validate_template_conformance

    REGISTRY.extend([
        citation_entry(_REFS / "source-tiers.yaml"),
        stm_entry(_REFS / "source-tiers.yaml"),
        fl_entry(_REFS / "forbidden-language.md"),
        ct_entry(_REFS / "crisis-resources.md"),
        validate_evidence_label_coverage,
        validate_bibliography_integrity,
        validate_template_conformance,
    ])


# Auto-populate on import unless tests explicitly clear the registry.
populate_registry()
