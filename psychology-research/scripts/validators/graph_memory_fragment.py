"""Graph-memory fragment validator (BLOCK).

Validates a graph-memory fragment file against the local_context contract
(references/graph-memory-contract.md): 'fragments' is a list; every fragment is
type 'local_context', carries the required edge fields, and is NEVER labeled
VERIFIED — a graph-sourced claim can only ever be context local to this effort,
not external evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.validators import Severity, ValidatorResult

_REQUIRED_FIELDS = ("source", "target", "edge_type", "valid_at", "fact")
_FORBIDDEN_STATUS = "VERIFIED"
_NAME = "graph_memory_fragment"


def validate_graph_memory_fragment(fragment_path: Path) -> ValidatorResult:
    try:
        data = json.loads(fragment_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ValidatorResult(
            name=_NAME, severity=Severity.BLOCK,
            findings=[f"unreadable or invalid JSON: {exc}"],
        )

    fragments = data.get("fragments") if isinstance(data, dict) else None
    if not isinstance(fragments, list):
        return ValidatorResult(
            name=_NAME, severity=Severity.BLOCK,
            findings=["missing or non-list 'fragments' array"],
        )

    findings: list[str] = []
    for i, frag in enumerate(fragments):
        if not isinstance(frag, dict):
            findings.append(f"fragment[{i}] is not an object")
            continue
        if frag.get("type") != "local_context":
            findings.append(
                f"fragment[{i}] type must be 'local_context', got {frag.get('type')!r}"
            )
        for field in _REQUIRED_FIELDS:
            if not frag.get(field):
                findings.append(f"fragment[{i}] missing required field '{field}'")
        if frag.get("status") == _FORBIDDEN_STATUS:
            findings.append(
                f"fragment[{i}] status VERIFIED is forbidden for graph-sourced "
                "local_context claims"
            )

    severity = Severity.BLOCK if findings else Severity.PASS
    return ValidatorResult(name=_NAME, severity=severity, findings=findings)
