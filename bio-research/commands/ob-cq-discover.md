---
description: Browse, filter, and inspect competency questions from the HuggingFace dataset
argument-hint: "[filter | cq_id | --analysis]"
---

# Bio-Research: Discover Competency Questions

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

You are browsing the competency questions catalog using the `biosciences-cq-discover` skill. This command loads CQ definitions from the `open-biosciences/biosciences-competency-questions-sample` HuggingFace dataset and presents them in three modes: summary table, filtered list, or detailed single-CQ view.

## Usage

```
/ob-cq-discover $ARGUMENTS
```

Where `$ARGUMENTS` is one of:
- **(empty)** -- show all 15 CQs as a summary table
- **Filter term** -- filter by category, reasoning type, complexity, disease area, or API name
- **CQ ID** -- e.g., `cq1`, `cq14` -- show full details for a specific CQ
- **`--analysis`** -- show cross-CQ analytics (API coverage, reasoning distribution, complexity breakdown)

## Workflow

### Step 1: Parse Arguments

Determine the mode from `$ARGUMENTS`:
- No arguments → Mode 1 (Summary Table)
- Matches a `cq_id` pattern (e.g., `cq1`, `cq14`) → Mode 3 (Detail View)
- `--analysis` → Cross-CQ Analysis
- Anything else → Mode 2 (Filtered List)

### Step 2: Execute Query

Use the `biosciences-cq-discover` skill to load data from HuggingFace via DuckDB and render the appropriate output.

### Step 3: Offer Next Steps

After displaying results, suggest:
- Run `/ob-cq-run <cq_id>` to execute a specific CQ against live MCP servers
- Run `/ob-cq-discover <filter>` to narrow results
- Run `/ob-cq-discover <cq_id>` to see full details

## Tips

- **No API keys needed**: This command only reads the public HuggingFace dataset
- **Quick overview**: Run with no arguments to see all 15 CQs at a glance
- **Find by API**: Use an API name like `STRING` or `ChEMBL` to find CQs that use that API
- **Detail view**: Use a CQ ID to see entities, edges, workflow steps, and gold standard path
