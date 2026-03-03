---
description: Run and validate a competency question from the HuggingFace dataset against live MCP servers
argument-hint: "<cq_id | list | all> [--publish] [--no-persist]"
---

# Bio-Research: Run Competency Question

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

You are executing a structured competency question (CQ) from the `open-biosciences/biosciences-competency-questions-sample` HuggingFace dataset using the `biosciences-cq-runner` skill. This command loads a CQ definition, delegates execution to the `biosciences-graph-builder` skill's Fuzzy-to-Fact protocol, validates results against the gold standard, persists results locally, and generates a validation report.

## Usage

```
/ob-cq-run $ARGUMENTS
```

Where `$ARGUMENTS` is one of:
- **CQ ID**: e.g., `cq1`, `cq14` -- run a specific competency question
- **`list`** -- show all available CQs and prompt for selection
- **`all`** -- batch-run all CQs with a summary table at the end

Optional flags (append after the CQ ID):
- **`--publish`** -- publish validation results to HuggingFace (requires HF_TOKEN)
- **`--no-persist`** -- skip local file persistence (dry-run testing)

## How It Works

```
  /ob-cq-run cq1
       |
  LOAD -----> Load CQ definition from HuggingFace dataset
       |        (fallback: local competency-questions-catalog.md)
  PREFLIGHT -> Verify MCP gateway connectivity
       |
  EXECUTE ---> Delegate workflow_steps to graph-builder
       |        (Fuzzy-to-Fact: Anchor → Enrich → Expand → Traverse)
  VALIDATE --> Compare results vs gold_standard_path + biolink_edges
       |        (entity matching, edge matching, path verdict)
  PERSIST ---> Save per-CQ results to local .ob-cq/ directory
       |        (skip if --no-persist)
  REPORT ----> Generate validation report (pass/fail per step)
       |
  PUBLISH ---> (Optional) Push results to HuggingFace
```

## Workflow

### Step 1: Parse Arguments

Parse `$ARGUMENTS` to determine:
- **Mode**: single CQ, list, or batch
- **CQ ID**: if single mode, extract the ID (e.g., `cq1`, `cq14`)
- **Flags**: `--publish`, `--no-persist`

If mode is `list`, display the CQ catalog table and prompt for selection.

### Step 2: Load CQ Definition

Load the CQ from the HuggingFace dataset:

```python
from datasets import load_dataset
ds = load_dataset("open-biosciences/biosciences-competency-questions-sample", split="train")
cq = [row for row in ds if row["cq_id"] == cq_id][0]
```

If the dataset load fails, fall back to parsing a local `competency-questions-catalog.md` if one exists in the working directory or a `biosciences-research/docs/` directory relative to the workspace root.

### Step 3: Preflight Checks

Verify the execution environment:
1. Test biosciences-mcp gateway connectivity
2. Check HF_TOKEN (warn if missing and --publish requested)
3. Verify all tools referenced by this CQ's workflow steps are available

If the gateway is not connected, abort and suggest running `/start`.

### Step 4: Execute Workflow Steps

Delegate each step from the CQ's `workflow_steps` to the `biosciences-graph-builder` skill following the Fuzzy-to-Fact protocol. Show progress as each step executes:

- Use MCP tools as primary, curl as fallback
- Chain step outputs (CURIEs resolved in step N feed into step N+1)
- Handle failures gracefully (skip and continue, never abort)
- Respect API rate limits (1s for STRING, 0.5s for NCBI)

### Step 5: Validate Results

Compare execution results against the CQ's gold standard:
- **Entity validation**: Did we resolve each `key_entity` to the expected CURIE?
- **Edge validation**: Did we discover each `biolink_edge`?
- **Path validation**: Does the discovered mechanism match `gold_standard_path`?
- **Score**: Compute pass/fail per dimension and overall verdict

### Step 6: Persist Results Locally

Unless `--no-persist` was specified, write per-CQ results to local files:

```
.ob-cq/
├── {cq_id}/
│   ├── results.json       # Full execution results (accumulator + metadata)
│   ├── entities.json      # Resolved entities with CURIEs
│   ├── edges.json         # Discovered BioLink edges
│   └── validation.json    # Gold standard comparison + scores
└── summary.json           # Batch run summary (when using /ob-cq-run all)
```

### Step 7: Present Validation Report

Output the full validation report following the template in the `biosciences-cq-runner` skill.

### Step 8: Publish (Optional)

If `--publish` was specified and HF_TOKEN is set:
- Confirm with user before publishing
- Push validation results to `open-biosciences/biosciences-cq-validations`

### Step 9: Offer Next Steps

Suggest follow-up actions:
- Run `/ob-report` to format a full evidence-graded report from the validated graph
- Run `/ob-review` to evaluate the report against 10 quality dimensions
- Run `/ob-publish` to generate the full publication pipeline
- Run `/ob-cq-run all` to validate all CQs as a regression suite
- Re-run `/ob-cq-run {id}` after fixing any identified issues

## Tips

- **Run `/start` first**: Verify MCP servers are connected before running CQs
- **Start with a simple CQ**: `cq1` (FOP Mechanism) has 6 steps and is a good first test
- **Batch mode for regression**: `all` mode validates the entire platform against 15 gold standards
- **No-persist for testing**: Use `--no-persist` when you want to validate without writing local files
- **Catalog corrections**: The validation report identifies CURIE discrepancies between the catalog and live APIs -- use these to improve the dataset
- **ChEMBL flakiness**: If ChEMBL steps fail with 500 errors, that is a known API issue, not a platform bug. The runner falls back to Open Targets automatically.
