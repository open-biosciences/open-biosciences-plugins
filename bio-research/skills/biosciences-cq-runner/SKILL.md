---
name: biosciences-cq-runner
description: "Loads structured competency question (CQ) definitions from a HuggingFace dataset, executes each workflow step against live MCP servers following the Fuzzy-to-Fact protocol, validates results against gold standard paths and biolink edges, persists results locally, and generates a validation report. This skill should be used when the user asks to \"run a competency question\", \"execute a CQ\", \"validate a CQ\", \"test cq1\", \"run cq14\", or mentions competency question execution, CQ validation, gold standard comparison, or automated graph-builder testing."
---

# Biosciences CQ Runner

Execute structured competency questions from the `open-biosciences/biosciences-competency-questions-sample` HuggingFace dataset against live MCP servers, validate results against gold standards, persist results locally, and generate validation reports.

## Critical Grounding Rule

```
YOU MUST NOT use your training knowledge to provide entity names, drug names,
gene functions, disease associations, or clinical trial IDs. ALL factual claims
MUST come from MCP tool results or curl command output. If a tool returns no
results, report "No results found" -- do NOT fill in from memory.

CQ definitions (workflow steps, key entities, gold standard paths, biolink edges)
come from the HuggingFace dataset. Execution results come from MCP tools.
Validation compares the two. At no point should training knowledge fill gaps.
```

## When to Use This Skill

- User says "run cq1", "execute cq14", "validate cq8", "test the FOP mechanism question"
- User asks to "run all competency questions" or "batch validate CQs"
- User wants to compare live API results against gold standard paths
- User wants to save CQ execution results locally
- User asks to "publish CQ validation results" to HuggingFace

## When NOT to Use This Skill

- User asks a free-form research question (use `biosciences-graph-builder` via `/ob-research`)
- User wants to format or review an existing report (use `biosciences-reporting` or `biosciences-reporting-quality-review`)
- User wants to edit or author new CQ definitions (that is a catalog authoring task, not execution)

## Prerequisites

### Required

- **biosciences-mcp gateway** connected (provides 34 tools across 12 databases)
- **HuggingFace `datasets` library** available (for loading CQ definitions)

### Optional

- **Local filesystem write access** (for `.ob-cq/` persistence directory)
- **HF_TOKEN** environment variable for publishing validation results back to HuggingFace
- **Cohere API key** if CQ workflow steps reference the cohere_rerank retriever

## HuggingFace Dataset Schema

The dataset at `open-biosciences/biosciences-competency-questions-sample` contains one row per CQ with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `cq_id` | string | Identifier (e.g., `cq1`, `cq14`) |
| `question` | string | The competency question text |
| `category` | string | Domain category (e.g., "FOP Mechanism", "Synthetic Lethality") |
| `group_id` | string | Persistence namespace identifier (e.g., `cq1-fop-mechanism`) |
| `key_entities` | list[dict] | Entities with `name`, `curie`, `role` fields |
| `workflow_steps` | list[dict] | Ordered API calls with `phase`, `tool`, `params`, `expected_output` |
| `gold_standard_path` | string | Expected mechanism path as text |
| `biolink_edges` | list[dict] | Expected edges with `source`, `target`, `type` fields |
| `source` | string | Provenance (e.g., "DrugMechDB", "Feng et al. 2022", "Original") |

## Execution Flow

```
                      /ob-cq-run cq1
                          |
                +---------v----------+
                | 1. LOAD CQ         |  Load definition from HuggingFace dataset
                |    definition      |  Parse workflow_steps, key_entities, gold_standard
                +---------+----------+
                          |
                +---------v----------+
                | 2. PREFLIGHT       |  Verify MCP gateway, env vars
                |    checks          |  Report what is available vs missing
                +---------+----------+
                          |
                +---------v----------+
                | 3. EXECUTE         |  Run each workflow_step against live MCP servers
                |    workflow        |  Capture results, handle failures gracefully
                +---------+----------+
                          |
                +---------v----------+
                | 4. VALIDATE        |  Compare live results vs gold_standard_path
                |    results         |  Match entities, edges, CURIEs
                +---------+----------+
                          |
                +---------v----------+
                | 5. PERSIST         |  PERSIST locally
                |    locally         |  to .ob-cq/ directory
                +---------+----------+
                          |
                +---------v----------+
                | 6. REPORT          |  Generate validation report
                |    generation      |  Pass/fail per step, entity/edge matching
                +---------+----------+
                          |
                +---------v----------+
                | 7. PUBLISH         |  (Optional) Push validation results to HuggingFace
                |    (optional)      |  Requires HF_TOKEN
                +--------------------+
```

## Step 1: LOAD CQ Definition

### Loading from HuggingFace

```python
from datasets import load_dataset

ds = load_dataset("open-biosciences/biosciences-competency-questions-sample", split="train")

# Filter by CQ ID
cq_id = "cq1"  # from user input
cq_row = [row for row in ds if row["cq_id"] == cq_id]

if not cq_row:
    print(f"CQ '{cq_id}' not found in dataset. Available: {[r['cq_id'] for r in ds]}")
    # Offer selection from available CQs
```

### CQ Selection Modes

**By ID** (direct execution):
```
/ob-cq-run cq1
/ob-cq-run cq14
```

**By list** (interactive selection):
```
/ob-cq-run list
```

Display a table of all available CQs:

```
Available Competency Questions:

| ID   | Category              | Question Summary                                | Source          |
|------|-----------------------|-------------------------------------------------|-----------------|
| cq1  | FOP Mechanism         | Palovarotene mechanism for FOP                  | DrugMechDB      |
| cq2  | FOP Repurposing       | BMP pathway drug repurposing                    | DrugMechDB      |
| cq3  | AD Gene Networks      | Alzheimer's gene-protein interactions           | DALK (Li et al.)|
| ...  | ...                   | ...                                             | ...             |
| cq15 | CAR-T Regulatory      | FDA/EMA milestone velocity                      | Original        |

Enter a CQ ID to run (e.g., cq1), or 'all' to run batch validation:
```

**Batch mode** (run all CQs):
```
/ob-cq-run all
```

Runs every CQ sequentially. Produces a summary table at the end. Use for regression testing or full platform validation.

## Step 2: PREFLIGHT Checks

Before executing any workflow steps, verify the execution environment:

```
Preflight Check for CQ: cq1 (FOP Mechanism)
---------------------------------------------
[PASS] biosciences-mcp gateway ........... connected (hgnc_search_genes test OK)
[WARN] HF_TOKEN .......................... not set (publish step will be skipped)
[PASS] COHERE_API_KEY .................... set (cohere_rerank available)

Tools required by this CQ's workflow:
  [PASS] chembl_search_compounds ......... available
  [PASS] chembl_get_compound ............. available
  [PASS] hgnc_get_gene ................... available
  [PASS] opentargets_get_associations .... available

Ready to execute 6 workflow steps.
```

### Preflight Logic

1. **Test MCP gateway**: Call `hgnc_search_genes` with `{"query": "TP53", "slim": true, "page_size": 1}`. If this fails, abort with guidance.
2. **Check HF_TOKEN**: If not set, note that Step 7 (PUBLISH) will be skipped.
3. **Parse required tools**: Extract unique tool names from the CQ's `workflow_steps`. Verify each is callable via the gateway.
4. **Report readiness**: Show pass/warn/fail for each check. Proceed if gateway is available. Abort only if gateway is down.

## Step 3: EXECUTE Workflow Steps

> **Note:** The CQ runner delegates execution to the `biosciences-graph-builder` skill. Each workflow step maps to a phase of the Fuzzy-to-Fact protocol. The runner provides the structured CQ definition (entities, workflow steps, gold standard); graph-builder handles the actual MCP tool calls.

Execute each step from `workflow_steps` in order, following the Fuzzy-to-Fact protocol. Show progress as each step runs.

### Execution Pattern

For each `workflow_step` in the CQ definition:

```
Step 1/6: ANCHOR - chembl_search_compounds("palovarotene")
  Calling mcp__biosciences-mcp__chembl_search_compounds...
  Result: CHEMBL:2105648 (Palovarotene, Max Phase 4)
  Status: SUCCESS
  Duration: 1.2s

Step 2/6: ENRICH - chembl_get_compound("CHEMBL:2105648")
  Calling mcp__biosciences-mcp__chembl_get_compound...
  Result: MW=414.55, Indications=[Dry Eye Syndromes, Myositis Ossificans, ...]
  Status: SUCCESS
  Duration: 0.8s

Step 3/6: MECHANISM - curl ChEMBL /mechanism
  Calling curl...
  Result: AGONIST -> CHEMBL:2003 (Retinoic acid receptor gamma)
  Status: SUCCESS
  Duration: 0.6s

Step 4/6: ANCHOR - hgnc_get_gene("HGNC:171")
  Calling mcp__biosciences-mcp__hgnc_get_gene...
  Result: ACVR1, activin A receptor type 1, 2q24.1
  Status: SUCCESS
  Duration: 0.4s

Step 5/6: EXPAND - opentargets_get_associations("ENSG00000115170")
  Calling mcp__biosciences-mcp__opentargets_get_associations...
  Result: FOP (MONDO:0007606, score=0.816)
  Status: SUCCESS
  Duration: 1.1s

Step 6/6: PERSIST - save to .ob-cq/cq1/
  [Deferred to Step 5 of execution flow]
  Status: PENDING
```

### Tool Call Dispatch

Map each workflow step's `tool` field to the correct MCP call:

| Workflow Step Tool | MCP Call |
|--------------------|----------|
| `hgnc_search_genes` | `mcp__biosciences-mcp__hgnc_search_genes` |
| `hgnc_get_gene` | `mcp__biosciences-mcp__hgnc_get_gene` |
| `uniprot_search_proteins` | `mcp__biosciences-mcp__uniprot_search_proteins` |
| `uniprot_get_protein` | `mcp__biosciences-mcp__uniprot_get_protein` |
| `chembl_search_compounds` | `mcp__biosciences-mcp__chembl_search_compounds` |
| `chembl_get_compound` | `mcp__biosciences-mcp__chembl_get_compound` |
| `chembl_get_compounds_batch` | `mcp__biosciences-mcp__chembl_get_compounds_batch` |
| `opentargets_search_targets` | `mcp__biosciences-mcp__opentargets_search_targets` |
| `opentargets_get_target` | `mcp__biosciences-mcp__opentargets_get_target` |
| `opentargets_get_associations` | `mcp__biosciences-mcp__opentargets_get_associations` |
| `string_search_proteins` | `mcp__biosciences-mcp__string_search_proteins` |
| `string_get_interactions` | `mcp__biosciences-mcp__string_get_interactions` |
| `string_get_network_image_url` | `mcp__biosciences-mcp__string_get_network_image_url` |
| `biogrid_search_genes` | `mcp__biosciences-mcp__biogrid_search_genes` |
| `biogrid_get_interactions` | `mcp__biosciences-mcp__biogrid_get_interactions` |
| `ensembl_search_genes` | `mcp__biosciences-mcp__ensembl_search_genes` |
| `ensembl_get_gene` | `mcp__biosciences-mcp__ensembl_get_gene` |
| `ensembl_get_transcript` | `mcp__biosciences-mcp__ensembl_get_transcript` |
| `entrez_search_genes` | `mcp__biosciences-mcp__entrez_search_genes` |
| `entrez_get_gene` | `mcp__biosciences-mcp__entrez_get_gene` |
| `entrez_get_pubmed_links` | `mcp__biosciences-mcp__entrez_get_pubmed_links` |
| `pubchem_search_compounds` | `mcp__biosciences-mcp__pubchem_search_compounds` |
| `pubchem_get_compound` | `mcp__biosciences-mcp__pubchem_get_compound` |
| `iuphar_search_ligands` | `mcp__biosciences-mcp__iuphar_search_ligands` |
| `iuphar_get_ligand` | `mcp__biosciences-mcp__iuphar_get_ligand` |
| `iuphar_search_targets` | `mcp__biosciences-mcp__iuphar_search_targets` |
| `iuphar_get_target` | `mcp__biosciences-mcp__iuphar_get_target` |
| `wikipathways_search_pathways` | `mcp__biosciences-mcp__wikipathways_search_pathways` |
| `wikipathways_get_pathway` | `mcp__biosciences-mcp__wikipathways_get_pathway` |
| `wikipathways_get_pathways_for_gene` | `mcp__biosciences-mcp__wikipathways_get_pathways_for_gene` |
| `wikipathways_get_pathway_components` | `mcp__biosciences-mcp__wikipathways_get_pathway_components` |
| `clinicaltrials_search_trials` | `mcp__biosciences-mcp__clinicaltrials_search_trials` |
| `clinicaltrials_get_trial` | `mcp__biosciences-mcp__clinicaltrials_get_trial` |
| `clinicaltrials_get_trial_locations` | `mcp__biosciences-mcp__clinicaltrials_get_trial_locations` |
| `curl` | Execute via bash (for ChEMBL /mechanism, Open Targets GraphQL, STRING enrichment) |

### Chaining Step Outputs

Workflow steps are ordered. Later steps may reference outputs from earlier steps:

- If step N resolves a CURIE (e.g., `CHEMBL:2105648`), step N+1 uses that CURIE as input
- If step N returns an Ensembl ID from HGNC cross-references, step N+2 passes it to Open Targets
- Maintain a **step results accumulator** that maps entity names to resolved CURIEs

```
accumulator = {
    "Palovarotene": {"curie": "CHEMBL:2105648", "phase": 4},
    "ACVR1": {"curie": "HGNC:171", "ensembl": "ENSG00000115170", "uniprot": "Q04771"},
    "RARG": {"curie": "HGNC:9866", "ensembl": "ENSG00000172819", "uniprot": "P13631"},
    "FOP": {"curie": "MONDO:0007606", "score": 0.816}
}
```

### Error Handling per Step

Each step can produce one of four outcomes:

| Outcome | Action | Report Status |
|---------|--------|---------------|
| **SUCCESS** | Store result in accumulator, proceed | PASS |
| **API_ERROR** | Log error, attempt fallback (curl if MCP failed, or vice versa), then skip if fallback also fails | SKIP (with reason) |
| **NO_RESULTS** | Log that the API returned empty results, proceed | WARN (entity unresolved) |
| **TIMEOUT** | Log timeout after 30s, skip step, proceed | SKIP (timeout) |

```
CRITICAL: Never abort the entire CQ on a single step failure.
Skip the failed step, record the failure, and continue.
The validation report will show which steps succeeded and which did not.
```

### Fallback Patterns

| Primary (MCP) | Fallback (curl) | Trigger |
|---------------|-----------------|---------|
| `chembl_get_compound` | `curl ChEMBL /molecule/{ID}` | 500 error (common) |
| `chembl_search_compounds` | `curl ChEMBL /molecule/search?q={query}` | Gateway unavailable |
| `opentargets_get_associations` | Open Targets GraphQL `associatedDiseases` | MCP error |
| `clinicaltrials_search_trials` | `curl ClinicalTrials.gov /v2/studies` | Cloudflare block |
| `string_get_interactions` | `biogrid_get_interactions` | < 3 interactions returned |

### Rate Limiting

Respect per-API rate limits during execution:

| API | Limit | Mitigation |
|-----|-------|------------|
| HGNC | 10 req/s | No delay needed for single CQ |
| Ensembl | 15 req/s | No delay needed |
| STRING | 1 req/s | Add 1s delay between STRING calls |
| NCBI | 3 req/s | Add 0.5s delay between Entrez calls |
| Open Targets | ~5 req/s | Add 0.2s delay |
| ClinicalTrials.gov | Varies | Use curl for reliability |
| ChEMBL | 10 req/s | No delay needed |

## Step 4: VALIDATE Results

Compare the live execution results against the CQ's gold standard definition.

### Entity Validation

For each entity in `key_entities`, check if it was resolved to the expected CURIE:

```
Entity Validation:
| Entity       | Expected CURIE   | Resolved CURIE   | Match |
|--------------|------------------|------------------|-------|
| Palovarotene | CHEMBL:2105648   | CHEMBL:2105648   | EXACT |
| RARG         | HGNC:9866        | HGNC:9866        | EXACT |
| ACVR1        | HGNC:171         | HGNC:171         | EXACT |
| FOP          | MONDO:0007606    | MONDO:0007606    | EXACT |
```

Match categories:
- **EXACT**: Resolved CURIE matches expected CURIE exactly
- **EQUIVALENT**: Different CURIE prefix but same entity (e.g., `CHEMBL:2105648` vs `CHEMBL2105648` or `MONDO_0007606` vs `MONDO:0007606`)
- **PARTIAL**: Entity found but with a different CURIE (possible data version difference)
- **MISSING**: Entity not resolved after all attempts
- **EXTRA**: Entity discovered that is not in the gold standard (not a failure -- may be a bonus finding)

### Edge Validation

For each edge in `biolink_edges`, check if a corresponding relationship was discovered:

```
Edge Validation:
| Source           | Target         | Expected Type                       | Found | Match |
|------------------|----------------|-------------------------------------|-------|-------|
| CHEMBL:2105648   | HGNC:9866      | biolink:agonist_of                  | Yes   | EXACT |
| HGNC:9866        | HGNC:171       | biolink:regulates                   | Yes   | EXACT |
| HGNC:171         | MONDO:0007606  | biolink:gene_associated_with_condition | Yes | EXACT |
```

Edge match categories:
- **EXACT**: Source, target, and type all match
- **TYPE_MISMATCH**: Source and target match but edge type differs (e.g., `regulates` vs `interacts_with`)
- **DIRECTION_REVERSED**: Same entities but source/target swapped
- **MISSING**: Edge not found in execution results
- **EXTRA**: Edge discovered that is not in the gold standard

### Gold Standard Path Validation

Compare the overall mechanism path:

```
Gold Standard Path:
  Drug(Palovarotene) --[agonist]--> Protein(RARG) --[regulates]--> Protein(ACVR1) --[causes]--> Disease(FOP)

Discovered Path:
  Drug(CHEMBL:2105648) --[AGONIST]--> Protein(CHEMBL:2003/HGNC:9866) --[regulates BMP signaling]--> Protein(HGNC:171) --[gene_associated_with_condition]--> Disease(MONDO:0007606)

Path Verdict: VALIDATED (all hops confirmed by API evidence)
```

Path verdicts:
- **VALIDATED**: All hops in the gold standard path were confirmed by API evidence
- **PARTIAL**: Some hops confirmed, others missing or unverifiable
- **REFUTED**: API evidence contradicts the gold standard path
- **INCONCLUSIVE**: Not enough data to confirm or deny

### Scoring

Compute a validation score for the CQ:

```
CQ Validation Score:
  Entity Resolution:  4/4  (100%)
  Edge Discovery:     3/3  (100%)
  Path Validation:    VALIDATED
  Steps Completed:    6/6  (100%)
  Overall:            PASS
```

Thresholds:
- **PASS**: Entity resolution >= 80% AND edge discovery >= 70% AND path != REFUTED
- **PARTIAL PASS**: Entity resolution >= 50% OR edge discovery >= 50%
- **FAIL**: Entity resolution < 50% AND edge discovery < 50%, OR path == REFUTED

## Step 5: PERSIST Locally

Persist the discovered graph and validation results to a local `.ob-cq/` directory.

### Output Directory Structure

```
.ob-cq/{cq_id}/
  results.json       # Full execution record (graph_data + metadata)
  entities.json      # Resolved entities with CURIEs
  edges.json         # BioLink edges discovered
  validation.json    # Gold standard comparison results
```

### Graph Construction

Build the graph from execution results:

```python
graph_data = {
    "cq_id": "cq1",
    "question": "By what mechanism does Palovarotene treat FOP?",
    "validation_status": "PASS",
    "execution_date": "2026-03-02",
    "nodes": [
        {
            "id": "CHEMBL:2105648",
            "type": "biolink:SmallMolecule",
            "label": "Palovarotene",
            "properties": {"max_phase": 4, "molecular_weight": 414.55}
        },
        {
            "id": "HGNC:9866",
            "type": "biolink:Gene",
            "label": "RARG",
            "properties": {"symbol": "RARG", "name": "retinoic acid receptor gamma", "ensembl": "ENSG00000172819", "uniprot": "P13631", "location": "12q13.13"}
        },
        {
            "id": "HGNC:171",
            "type": "biolink:Gene",
            "label": "ACVR1",
            "properties": {"symbol": "ACVR1", "name": "activin A receptor type 1", "ensembl": "ENSG00000115170", "uniprot": "Q04771", "location": "2q24.1"}
        },
        {
            "id": "MONDO:0007606",
            "type": "biolink:Disease",
            "label": "FOP",
            "properties": {"name": "fibrodysplasia ossificans progressiva"}
        }
    ],
    "edges": [
        {"source": "CHEMBL:2105648", "target": "HGNC:9866", "type": "biolink:agonist_of"},
        {"source": "HGNC:9866", "target": "HGNC:171", "type": "biolink:regulates"},
        {"source": "HGNC:171", "target": "MONDO:0007606", "type": "biolink:gene_associated_with_condition"}
    ],
    "metadata": {
        "source_dataset": "open-biosciences/biosciences-competency-questions-sample",
        "tools_used": ["chembl_search_compounds", "chembl_get_compound", "hgnc_get_gene", "opentargets_get_associations"],
        "validation_score": {"entities": "4/4", "edges": "3/3", "path": "VALIDATED"}
    }
}
```

### Local File Persistence

```python
import json
import os

output_dir = f".ob-cq/{cq_id}"
os.makedirs(output_dir, exist_ok=True)

# Full execution record
with open(f"{output_dir}/results.json", "w") as f:
    json.dump(graph_data, f, indent=2)

# Resolved entities only
with open(f"{output_dir}/entities.json", "w") as f:
    json.dump(graph_data["nodes"], f, indent=2)

# BioLink edges only
with open(f"{output_dir}/edges.json", "w") as f:
    json.dump(graph_data["edges"], f, indent=2)

# Gold standard comparison
with open(f"{output_dir}/validation.json", "w") as f:
    json.dump({
        "cq_id": cq_id,
        "execution_date": graph_data["execution_date"],
        "validation_status": graph_data["validation_status"],
        "entity_scores": graph_data["metadata"]["validation_score"],
        "discrepancies": []
    }, f, indent=2)
```

### Pre-Emit Validation

Before persisting, verify all gene nodes have the 5 required fields:

```
Required Gene Node Fields:
  - symbol     (from hgnc_get_gene)
  - name       (from hgnc_get_gene)
  - ensembl    (ENSG... from hgnc_get_gene cross-refs)
  - uniprot    (from hgnc_get_gene cross-refs)
  - location   (from hgnc_get_gene)

If any gene node is missing fields, issue the necessary hgnc_get_gene call
to fill them BEFORE persisting. Do NOT persist incomplete gene nodes.
```

## Step 6: REPORT Generation

Generate a structured validation report.

### Validation Report Template

```markdown
# CQ Validation Report: {cq_id}

**Date**: {execution_date}
**Question**: {question}
**Category**: {category}
**Source**: {source}
**group_id**: {group_id}
**Overall Status**: {PASS | PARTIAL PASS | FAIL}

---

## Preflight

| Check | Status |
|-------|--------|
| biosciences-mcp gateway | {PASS/FAIL} |
| HF_TOKEN | {PASS/WARN: not set} |
| Required tools ({N}) | {N}/{N} available |

---

## Workflow Execution

| Step | Phase | Tool | Parameters | Status | Duration |
|------|-------|------|------------|--------|----------|
| 1/{N} | ANCHOR | chembl_search_compounds | "palovarotene" | PASS | 1.2s |
| 2/{N} | ENRICH | chembl_get_compound | "CHEMBL:2105648" | PASS | 0.8s |
| ... | ... | ... | ... | ... | ... |

**Steps completed**: {completed}/{total} ({percentage}%)
**Total duration**: {total_seconds}s

---

## Entity Validation

| Entity | Expected CURIE | Resolved CURIE | Match |
|--------|----------------|----------------|-------|
| {name} | {expected} | {resolved} | {EXACT/EQUIVALENT/PARTIAL/MISSING} |
| ... | ... | ... | ... |

**Entity resolution**: {matched}/{total} ({percentage}%)

---

## Edge Validation

| Source | Target | Expected Type | Found | Match |
|--------|--------|---------------|-------|-------|
| {source_curie} | {target_curie} | {biolink_type} | {Yes/No} | {EXACT/TYPE_MISMATCH/MISSING} |
| ... | ... | ... | ... | ... |

**Edge discovery**: {matched}/{total} ({percentage}%)

---

## Gold Standard Path

**Expected**:
{gold_standard_path}

**Discovered**:
{discovered_path}

**Verdict**: {VALIDATED | PARTIAL | REFUTED | INCONCLUSIVE}
**Evidence**: {brief explanation citing specific tool results}

---

## Discovered Graph

**Nodes**: {node_count}
**Edges**: {edge_count}
**Persisted locally**: {Yes (.ob-cq/{cq_id}/) | No (--no-persist)}

### Nodes
| ID | Type | Label | Key Properties |
|----|------|-------|----------------|
| {curie} | {biolink_type} | {label} | {properties_summary} |

### Edges
| Source | Target | Type | Properties |
|--------|--------|------|------------|
| {source} | {target} | {type} | {props} |

---

## Discrepancies

{List any differences between gold standard and live results.}
{Note CURIE corrections needed in the catalog.}
{Note extra entities or edges discovered beyond the gold standard.}

---

## Tools Used

| Phase | Tool | Purpose | Result |
|-------|------|---------|--------|
| {phase} | {tool_name}({params}) | {purpose} | {brief_result} |

---

## Score Summary

| Dimension | Score |
|-----------|-------|
| Entity Resolution | {N}/{M} ({pct}%) |
| Edge Discovery | {N}/{M} ({pct}%) |
| Path Validation | {verdict} |
| Steps Completed | {N}/{M} ({pct}%) |
| **Overall** | **{PASS / PARTIAL PASS / FAIL}** |
```

### Batch Report Template (for `/ob-cq-run all`)

When running all CQs, produce a summary table after individual reports:

```markdown
# CQ Batch Validation Summary

**Date**: {execution_date}
**CQs Executed**: {count}
**Total Duration**: {total_minutes} minutes

| CQ | Category | Entities | Edges | Path | Steps | Overall |
|----|----------|----------|-------|------|-------|---------|
| cq1 | FOP Mechanism | 4/4 (100%) | 3/3 (100%) | VALIDATED | 6/6 | PASS |
| cq2 | FOP Repurposing | 3/4 (75%) | 2/3 (67%) | PARTIAL | 4/5 | PARTIAL |
| ... | ... | ... | ... | ... | ... | ... |

**Summary**: {pass_count} PASS, {partial_count} PARTIAL PASS, {fail_count} FAIL
**Platform Health**: {pass_count}/{total} CQs fully validated ({pct}%)
```

## Step 7: PUBLISH to HuggingFace (Optional)

If `HF_TOKEN` is set and the user requests publication:

### What Gets Published

Push validation results as a new dataset revision to HuggingFace:

```python
from datasets import Dataset

validation_records = [
    {
        "cq_id": "cq1",
        "execution_date": "2026-03-02",
        "overall_status": "PASS",
        "entity_score": "4/4",
        "edge_score": "3/3",
        "path_verdict": "VALIDATED",
        "steps_completed": "6/6",
        "duration_seconds": 5.3,
        "discrepancies": [],
        "graph_json": json.dumps(graph_data),
        "report_markdown": report_text
    }
]

ds = Dataset.from_list(validation_records)
ds.push_to_hub(
    "open-biosciences/biosciences-cq-validations",
    token=os.environ["HF_TOKEN"],
    commit_message=f"Validation run: {cq_id} on {execution_date}"
)
```

### Publication Confirmation

Always ask before publishing:

```
Validation complete for cq1.
Publish results to HuggingFace (open-biosciences/biosciences-cq-validations)?
This requires HF_TOKEN and will create a public dataset revision.
[y/n]
```

## Example Invocations

### Run a single CQ

```
User: /ob-cq-run cq1
```

Loads cq1 (FOP Mechanism), runs 6 workflow steps, validates against gold standard, persists results to `.ob-cq/cq1/`, outputs validation report.

### Run a CQ by topic

```
User: /ob-cq-run cq14
```

Loads cq14 (Feng et al. Synthetic Lethality), runs TP53/TYMS validation, checks BioGRID ORCS, discovers approved drugs, finds clinical trials, validates against gold standard path.

### List available CQs

```
User: /ob-cq-run list
```

Displays the full CQ catalog table, prompts for selection.

### Batch validation

```
User: /ob-cq-run all
```

Runs all 15 CQs sequentially. Generates individual reports plus a batch summary table. Use for regression testing after MCP server changes.

### Run and publish

```
User: /ob-cq-run cq8 --publish
```

Runs cq8 (ARID1A Synthetic Lethality), generates validation report, then publishes results to HuggingFace.

### Run without persistence

```
User: /ob-cq-run cq11 --no-persist
```

Runs cq11 (p53-MDM2-Nutlin) but skips the local persistence step. Useful for testing without side effects.

## Error Handling Patterns

### MCP Gateway Unavailable

```
ERROR: biosciences-mcp gateway is not connected.

The CQ runner requires the biosciences-mcp gateway to execute workflow steps.
Verify the gateway is running:
  - Check .mcp.json for biosciences-mcp URL
  - Test: curl -s https://biosciences-mcp.fastmcp.app/health

Alternative: Run /start to check all connected MCP servers.
```

**Action**: Abort. The CQ runner cannot function without the gateway.

### Single Step Failure (Non-Fatal)

```
Step 3/6: MECHANISM - curl ChEMBL /mechanism
  ERROR: HTTP 500 from ChEMBL API
  Fallback: Attempting Open Targets knownDrugs query...
  Fallback Result: AGONIST -> Retinoic acid receptor gamma
  Status: PASS (via fallback)
```

**Action**: Try fallback. If fallback also fails, mark step as SKIP and continue.

### ChEMBL 500 Errors

ChEMBL detail endpoints (`chembl_get_compound`, `/mechanism`) frequently return 500 errors. This is a known API reliability issue, not a bug.

```
Step 2/6: ENRICH - chembl_get_compound("CHEMBL:2105648")
  ERROR: HTTP 500 from ChEMBL
  This is a known ChEMBL API issue.
  Attempting alternative: opentargets_get_target for drug metadata...
  Status: SKIP (ChEMBL 500, partial data from Open Targets)
```

**Action**: Switch to Open Targets. Do not retry ChEMBL more than once.

### HuggingFace Dataset Load Failure

```
ERROR: Failed to load dataset 'open-biosciences/biosciences-competency-questions-sample'
  Reason: {error_message}

Possible causes:
  1. Network issue -- check internet connectivity
  2. Dataset not found -- verify the dataset name on huggingface.co
  3. Private dataset -- set HF_TOKEN with read access

Falling back to local CQ catalog at:
  /home/donbr/open-biosciences/biosciences-research/docs/competency-questions-catalog.md
```

**Action**: If HuggingFace load fails, fall back to parsing the local `competency-questions-catalog.md` file. The local catalog contains the same CQ definitions in a less structured format. Parse the workflow steps, key entities, and gold standard paths from the markdown.

### CQ ID Not Found

```
ERROR: CQ 'cq16' not found in dataset.
Available CQs: cq1, cq2, cq3, cq4, cq5, cq6, cq7, cq8, cq9, cq10, cq11, cq12, cq13, cq14, cq15

Did you mean one of these?
  cq6  - BRCA1 Regulatory Network
  cq16 - (does not exist)
```

**Action**: Show available CQs. Suggest closest match. Do not guess.

### Rate Limit Hit

```
Step 3/6: EXPAND - string_get_interactions("9606.ENSP00000251849")
  WARNING: STRING rate limit hit (429). Waiting 2s before retry...
  Retry successful.
  Status: PASS (after rate limit delay)
```

**Action**: Wait and retry once. If second attempt also rate-limited, skip the step.

## Integration with Other Commands

### Before CQ Runner

- Run `/start` to verify MCP server connectivity
- Ensure the biosciences-mcp gateway is connected

### After CQ Runner

The CQ runner produces a validation report and (optionally) a persisted graph. From there:

- Run `/ob-report` on the validation data to format a full evidence-graded report
- Run `/ob-review` on the report for 10-dimension quality assessment
- Run `/ob-publish` to generate the full 5-file publication pipeline
- Re-run `/ob-cq-run {id}` after fixing API issues to get an updated validation

### Relationship to `/ob-research`

| Aspect | `/ob-research` | `/ob-cq-run` |
|--------|----------------|----------|
| Input | Free-form question | Structured CQ from HuggingFace dataset |
| Workflow | Adaptive (Claude determines phases) | Prescribed (workflow_steps from dataset) |
| Validation | No gold standard | Compares against gold_standard_path and biolink_edges |
| Output | KG JSON + narrative | Validation report + KG JSON + scores |
| Use case | Exploratory research | Regression testing, platform validation |

## API Reliability Reference

Known API behaviors that affect CQ execution:

| API | Known Issues | Mitigation |
|-----|-------------|------------|
| ChEMBL `/mechanism` | Frequent 500 errors | Fallback to Open Targets `knownDrugs` |
| ChEMBL `get_compound` | Intermittent 500s on detail endpoint | Use `search_compounds` which is more reliable |
| STRING | 1 req/s rate limit | Add 1s delay between calls |
| ClinicalTrials.gov | Cloudflare blocks Python clients | Use curl for reliability |
| Open Targets | Pagination requires `index: 0` explicitly | Always include `page: {index: 0, size: N}` |
| BioGRID | Requires `BIOGRID_API_KEY` | Check env before calling |

## See Also

- **biosciences-graph-builder**: The underlying Fuzzy-to-Fact execution engine (Phases 1-6a)
- **biosciences-reporting**: Report formatting with evidence grading (Phase 6b)
- **biosciences-reporting-quality-review**: 10-dimension quality assessment
- **biosciences-publication-pipeline**: Full publication workflow (report, KG JSON, Synapse grounding, quality review, BioRxiv draft)
- **biosciences-clinical**: ClinicalTrials.gov and Open Targets association queries
- **biosciences-pharmacology**: ChEMBL, PubChem, IUPHAR drug queries
- **biosciences-genomics**: HGNC, Ensembl, NCBI gene resolution
- **biosciences-proteomics**: UniProt, STRING, BioGRID interaction queries

### Data References

- **CQ Definitions**: `open-biosciences/biosciences-competency-questions-sample` (HuggingFace)
- **CQ Catalog**: `biosciences-research/docs/competency-questions-catalog.md` (local fallback)
- **Local Persistence**: `.ob-cq/{cq_id}/` directory (results.json, entities.json, edges.json, validation.json)
- **Validation Results**: `open-biosciences/biosciences-cq-validations` (HuggingFace, optional publish target)
- **Existing Validations**: `biosciences-research/docs/competency-validations/` (prior manual runs)
