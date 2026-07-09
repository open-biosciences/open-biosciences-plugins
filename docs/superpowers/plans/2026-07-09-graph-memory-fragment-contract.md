# Graph-Memory Fragment Contract (SP-A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generic `local_context` graph-memory fragment contract to the psychology-research plugin — a documented JSON schema for graph-sourced context, a stdlib validator that enforces it (fragments are `local_context` and never `VERIFIED`), tests, and the `~~graph-memory` binding + Source-Hierarchy doc wiring.

**Architecture:** This is SP-A of the graph-memory bridge: the public, generic, reusable half. Any graph store (Graphiti/Neo4j/…) that emits the fragment shape can bind to the plugin's `~~graph-memory` socket via a **JSON file** — there is no live protocol here. A separate, private consumer (SP-B, out of scope for this plan) produces fragment files conforming to this contract. Authored upstream in `open-biosciences-plugins/psychology-research/` and propagated to the standalone marketplace mirror via `scripts/sync-from-marketplace.sh`.

**Tech Stack:** Python 3.11 stdlib only (`json`, `pathlib`, `tempfile`, `unittest`, `dataclasses`); Markdown docs; the existing `scripts/validators` `Severity` / `ValidatorResult` types.

## Global Constraints

- Stdlib-only Python 3.11; **no third-party runtime dependencies**.
- **Author upstream only.** The `psychology-research-plugins` mirror is synced with `rsync --delete`; never edit it directly — all edits land here in `open-biosciences-plugins/psychology-research/`.
- A graph-sourced fact is `source_tier: local_context` and its `status` is **never `VERIFIED`** (a graph fact is context local to this effort, not external evidence).
- Validator severities are locked: this validator is **BLOCK** on any violation, **PASS** otherwise.
- Generic contract only — no consumer-specific or domain-specific content in these files.

---

## File structure

| Path | Responsibility |
|---|---|
| `psychology-research/references/graph-memory-contract.md` | **New.** The fragment-file JSON schema + the `local_context`-never-`VERIFIED` rule + example. |
| `psychology-research/scripts/validators/graph_memory_fragment.py` | **New.** `validate_graph_memory_fragment(fragment_path) -> ValidatorResult` — schema + never-VERIFIED enforcement. |
| `psychology-research/scripts/tests/test_graph_memory_fragment.py` | **New.** Unit tests (valid, empty, wrong-type, missing-field, VERIFIED-violation, malformed-JSON). |
| `psychology-research/CONNECTORS.md` | **Modify.** `~~graph-memory` row + a fragment-input subsection. |
| `psychology-research/references/fuzzy-to-evidence.md` | **Modify.** Cross-link the contract from the Source-Hierarchy "Local context" row. |

All paths below are relative to the repo root. Commands run from `psychology-research/` (where the existing test suite runs).

---

### Task 1: The fragment contract document

**Files:**
- Create: `psychology-research/references/graph-memory-contract.md`

**Interfaces:**
- Produces: the canonical schema + rule that Task 2's validator enforces and Task 3's docs cross-link. Field names here (`fragments`, `type`, `source`, `target`, `edge_type`, `valid_at`, `fact`, `status`, `provenance`) are the contract Task 2 depends on.

- [ ] **Step 1: Write the contract doc**

Create `psychology-research/references/graph-memory-contract.md`:

````markdown
# Graph-Memory Fragment Contract

A `~~graph-memory` source (Graphiti/Neo4j or any graph store) may supply context to a
research run as a **fragment file**: a JSON document whose entries are graph-stored
relationship facts. This contract is tool-agnostic — any graph source that emits this
shape can bind to `~~graph-memory`. The binding is a file, not a live protocol.

## Load-bearing rule

A graph-sourced fact is **`local_context`**, never external evidence. It enters the
evidence packet as `source_tier: local_context`, and its `status` is **never `VERIFIED`**
— a graph fact is context local to this effort (often the very phenomenon under study),
not independent proof of a claim. A claim that ties a graph fragment to external
literature is labeled at the **weaker** of the two.

## Schema

```json
{
  "graph": "string",
  "snapshot_at": "ISO-8601",
  "fragments": [
    {
      "type": "local_context",
      "source": "string",
      "target": "string",
      "edge_type": "string",
      "valid_at": "ISO-8601",
      "fact": "string",
      "status": "SELF_REPORTED",
      "provenance": { "edge_uuid": "string" }
    }
  ]
}
```

- `type` is REQUIRED and must be exactly `"local_context"`.
- `source`, `target`, `edge_type`, `valid_at`, `fact` are REQUIRED and non-empty.
- `status` is OPTIONAL; if present it must never be `"VERIFIED"`.
- `provenance` is OPTIONAL.
- `snapshot_at` records when the fragment was exported, so a consumer can judge staleness.
- An empty `fragments` array is valid (no context to add).

## Validation

`scripts/validators/graph_memory_fragment.py` enforces this contract (BLOCK on violation):
`fragments` is a list; each fragment `type == "local_context"`; required fields present and
non-empty; `status` never `VERIFIED`. Run it before feeding a fragment file into a research
run.

## Direction

Read-only into the plugin. The plugin never writes back into the source graph; persisting
research outputs to a graph is the source system's concern, through its own write path.
````

- [ ] **Step 2: Verify the schema block is present**

Run: `cd psychology-research && grep -q '"fragments"' references/graph-memory-contract.md && echo OK`
Expected: prints `OK`. (This file introduces no `{{include:}}` markers, so the sync-time marker check — a CI concern on the expanded tree — is not exercised here.)

- [ ] **Step 3: Commit**

```bash
git add psychology-research/references/graph-memory-contract.md
git commit -m "docs: add graph-memory fragment contract (local_context schema)"
```

---

### Task 2: The fragment validator (TDD)

**Files:**
- Create: `psychology-research/scripts/validators/graph_memory_fragment.py`
- Test: `psychology-research/scripts/tests/test_graph_memory_fragment.py`

**Interfaces:**
- Consumes: `Severity`, `ValidatorResult` from `scripts.validators` (existing: `Severity.PASS|WARN|BLOCK`; `ValidatorResult(name, severity, findings)`).
- Produces: `validate_graph_memory_fragment(fragment_path: Path) -> ValidatorResult` (name `"graph_memory_fragment"`).

- [ ] **Step 1: Write the failing test**

Create `psychology-research/scripts/tests/test_graph_memory_fragment.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validators.graph_memory_fragment import validate_graph_memory_fragment
from scripts.validators import Severity


def _temp_json(obj) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(obj, f)
    f.close()
    return Path(f.name)


_GOOD_FRAGMENT = {
    "type": "local_context",
    "source": "A", "target": "B", "edge_type": "relation",
    "valid_at": "2026-07-09T09:00:00-07:00", "fact": "A and B share a bond.",
    "status": "SELF_REPORTED", "provenance": {"edge_uuid": "u1"},
}


class TestGraphMemoryFragment(unittest.TestCase):
    def test_valid_fragment_passes(self):
        path = _temp_json({"graph": "g", "snapshot_at": "2026-07-09", "fragments": [_GOOD_FRAGMENT]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.PASS)

    def test_empty_fragments_passes(self):
        path = _temp_json({"graph": "g", "snapshot_at": "2026-07-09", "fragments": []})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.PASS)

    def test_missing_fragments_array_blocks(self):
        path = _temp_json({"graph": "g"})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_wrong_type_blocks(self):
        frag = dict(_GOOD_FRAGMENT, type="primary")
        path = _temp_json({"fragments": [frag]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_missing_required_field_blocks(self):
        frag = dict(_GOOD_FRAGMENT)
        del frag["fact"]
        path = _temp_json({"fragments": [frag]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_verified_status_blocks(self):
        frag = dict(_GOOD_FRAGMENT, status="VERIFIED")
        path = _temp_json({"fragments": [frag]})
        r = validate_graph_memory_fragment(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_malformed_json_blocks(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        f.write("{ not json")
        f.close()
        r = validate_graph_memory_fragment(Path(f.name))
        self.assertEqual(r.severity, Severity.BLOCK)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd psychology-research && python3 -m pytest scripts/tests/test_graph_memory_fragment.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.validators.graph_memory_fragment'`.

- [ ] **Step 3: Write the validator**

Create `psychology-research/scripts/validators/graph_memory_fragment.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd psychology-research && python3 -m pytest scripts/tests/test_graph_memory_fragment.py -q`
Expected: PASS — 7 passed.

- [ ] **Step 5: Run the full suite to confirm no regression**

Run: `cd psychology-research && python3 -m pytest scripts/tests -q`
Expected: all prior tests still pass (32) + 7 new = 39 passed.

- [ ] **Step 6: Commit**

```bash
git add psychology-research/scripts/validators/graph_memory_fragment.py \
        psychology-research/scripts/tests/test_graph_memory_fragment.py
git commit -m "feat: add graph-memory fragment validator (local_context, never VERIFIED)"
```

---

### Task 3: Wire the contract into CONNECTORS.md + fuzzy-to-evidence.md

**Files:**
- Modify: `psychology-research/CONNECTORS.md`
- Modify: `psychology-research/references/fuzzy-to-evidence.md`

**Interfaces:**
- Consumes: the contract path `references/graph-memory-contract.md` (Task 1) and the validator path (Task 2).

- [ ] **Step 1: Update the `~~graph-memory` row in CONNECTORS.md**

In `psychology-research/CONNECTORS.md`, replace the `Local knowledge graph` row's "Primary Uses" cell so it reads:

```
| Local knowledge graph | `~~graph-memory` | (optional, user-configured) | Optional Graphiti/Neo4j persistence, prior evidence-packet retrieval, or a `local_context` graph fragment file (see `references/graph-memory-contract.md`) |
```

- [ ] **Step 2: Add a fragment-input subsection to CONNECTORS.md**

Immediately after the connectors table in `psychology-research/CONNECTORS.md`, add:

```markdown
### Graph-memory fragment input

A `~~graph-memory` source may supply context as a **fragment file** — a JSON document
conforming to `references/graph-memory-contract.md`. Its entries enter the evidence packet
as `source_tier: local_context` and can never be labeled `VERIFIED`: a graph-sourced claim
is context local to this effort, not external evidence. Validate a fragment file with
`scripts/validators/graph_memory_fragment.py` before ingestion.
```

- [ ] **Step 3: Cross-link the contract from the Source Hierarchy**

In `psychology-research/references/fuzzy-to-evidence.md`, in the "Source Hierarchy" table, replace the "Local context" row's "Use" cell so it reads:

```
| Local context | User docs, local memory files, project concepts, graph-memory fragments | User-provided thesis/context; not external evidence. Graph fragments follow `references/graph-memory-contract.md`. |
```

- [ ] **Step 4: Verify the suite is still green**

Run: `cd psychology-research && python3 -m pytest scripts/tests -q`
Expected: 39 passed. (These are doc-only edits with no new `{{include:}}` markers; the sync-time marker check remains CI's job on the expanded tree.)

- [ ] **Step 5: Commit**

```bash
git add psychology-research/CONNECTORS.md psychology-research/references/fuzzy-to-evidence.md
git commit -m "docs: bind graph-memory fragment contract into CONNECTORS + source hierarchy"
```

---

## Out of scope (explicit)

- **SP-B** (the private consumer that exports fragment files from a specific graph) — separate plan, separate repo.
- **Publish-gate packet enforcement** — cross-checking a fully assembled `evidence-packet.json` so a `local_context` source can never carry `VERIFIED` inside the seven-validator publish gate. This plan enforces the rule at the **fragment** boundary; extending it into the packet-level gate (which currently validates `report.md`, not the packet JSON) is a follow-on.
- Modality-canon coverage and the `template_conformance` mode-awareness fix — tracked separately as issues #9 and #8.

## Self-review notes

- **Spec coverage:** contract doc (Task 1) = schema + tier rule; validator + tests (Task 2) = "graph-sourced claims are `local_context`, never `VERIFIED`"; doc wiring (Task 3) = `~~graph-memory` binding as a fragment-file input. Packet-level gate integration is explicitly deferred above.
- **Placeholders:** none — every step carries the literal file content or command.
- **Type consistency:** `validate_graph_memory_fragment(Path) -> ValidatorResult`, name `"graph_memory_fragment"`, used identically in the test and validator; `Severity`/`ValidatorResult` match the existing `scripts/validators/__init__.py` definitions.
