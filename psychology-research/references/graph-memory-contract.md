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
