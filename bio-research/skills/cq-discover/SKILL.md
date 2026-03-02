---
name: cq-discover
description: "Browse, filter, and search the Open Biosciences competency questions catalog from HuggingFace. No API keys required. This skill should be used when the user asks to \"find competency questions\", \"browse CQs\", \"discover research questions\", \"list competency questions\", \"search CQs\", \"explore CQ catalog\", \"what questions can I research\", \"show me CQs about [topic]\", \"which CQs use [API]\", or mentions competency question discovery, CQ filtering, or research question browsing."
---

# CQ Discover

Browse, filter, and search the 15 competency questions in the Open Biosciences catalog. Data is loaded directly from HuggingFace via DuckDB -- no API keys required, no downloads needed.

## Data Source

```
Dataset: open-biosciences/biosciences-competency-questions-sample
Format:  Parquet on HuggingFace Hub
Rows:    15 competency questions (cq1-cq15)
Access:  Public, MIT license
```

```python
import duckdb

CQ_DATASET = "hf://datasets/open-biosciences/biosciences-competency-questions-sample/data/*.parquet"
con = duckdb.connect()
```

## Modes of Operation

This skill operates in three modes depending on the user's request:

### Mode 1: Summary Table (Browse/List)

When the user asks to browse, list, or see all CQs without a specific filter.

**Query:**
```sql
SELECT cq_id, question, category, disease_area, complexity, num_hops
FROM '{CQ_DATASET}'
ORDER BY cq_id;
```

**Output format** -- render as a markdown table:
```
| CQ   | Question (truncated to ~60 chars)           | Category               | Disease Area        | Complexity   | Hops |
|------|---------------------------------------------|------------------------|---------------------|--------------|------|
| cq1  | By what mechanism does Palovarotene treat... | Drug Mechanism of Action| Rare Disease (FOP)  | intermediate | 3    |
| cq2  | What other drugs targeting the BMP Signal... | Drug Repurposing       | Rare Disease (FOP)  | advanced     | 4    |
| ...  | ...                                         | ...                    | ...                 | ...          | ...  |
```

After the table, show a facet summary:
```
15 competency questions across 8 categories, 7 disease areas
Complexity: 8 intermediate, 7 advanced
Hops range: 2-5 (median 3)
```

### Mode 2: Filtered List

When the user specifies one or more filter criteria. Build the SQL WHERE clause dynamically from the user's request.

**Filterable columns:**

| Filter | Column | Type | Valid values |
|--------|--------|------|-------------|
| Category | `category` | string | Drug Mechanism of Action, Drug Repurposing, Gene-Protein Networks, Therapeutic Target Discovery, Signaling Cascades, Transcription Factor Networks, Multi-Hop Drug Repurposing, Synthetic Lethality, Drug Safety, Orphan Drug Discovery, Pathway Validation, Health Emergencies, Commercialization Analysis, Regulatory Analysis |
| Disease area | `disease_area` | string | Rare Disease (FOP), Neurodegeneration (Alzheimer's), Oncology (MAPK pathway), Oncology (Breast Cancer), Rare Disease (NGLY1), Oncology (Ovarian Cancer), Oncology (CML/ALL), Neurodegeneration (Huntington's), Oncology (p53-MDM2), Cross-disease, Oncology (TP53-mutant), Oncology/Autoimmune (CAR-T) |
| Reasoning type | `reasoning_type` | string | multi_hop_traversal, network_expansion, directed_traversal, bidirectional_expansion, federated_multi_hop, comparative_analysis, set_difference, aggregation, ranking, temporal_analysis |
| Complexity | `complexity` | string | intermediate, advanced |
| Num hops | `num_hops` | int | 2, 3, 4, 5 (supports range: `num_hops BETWEEN 2 AND 3`) |
| APIs used | `apis_used` | list[string] | HGNC, UniProt, STRING, BioGRID, ChEMBL, Open Targets, PubChem, IUPHAR, WikiPathways, ClinicalTrials.gov, Ensembl, Entrez |

**Example filter queries:**

```sql
-- CQs about oncology
SELECT cq_id, question, category, disease_area, complexity, num_hops
FROM '{CQ_DATASET}'
WHERE disease_area LIKE '%Oncology%'
ORDER BY cq_id;

-- Advanced CQs with 4+ hops
SELECT cq_id, question, category, disease_area, complexity, num_hops
FROM '{CQ_DATASET}'
WHERE complexity = 'advanced' AND num_hops >= 4
ORDER BY cq_id;

-- CQs that use STRING API
SELECT cq_id, question, category, disease_area
FROM '{CQ_DATASET}'
WHERE list_contains(apis_used, 'STRING')
ORDER BY cq_id;

-- CQs with synthetic lethality reasoning
SELECT cq_id, question, disease_area, num_hops
FROM '{CQ_DATASET}'
WHERE reasoning_type = 'multi_hop_traversal' AND category LIKE '%Synthetic%'
ORDER BY cq_id;
```

When filtering by APIs, use `list_contains(apis_used, 'API_NAME')` since `apis_used` is a list column. For multiple APIs, chain with AND:
```sql
WHERE list_contains(apis_used, 'ChEMBL') AND list_contains(apis_used, 'ClinicalTrials.gov')
```

**Output format** -- same summary table as Mode 1, but only matching rows. Always state the filter applied and the match count:
```
Showing 5 of 15 CQs matching: disease_area LIKE '%Oncology%'
```

### Mode 3: Detailed View (Single CQ)

When the user asks about a specific CQ by ID (e.g., "show me cq8" or "details for cq1").

**Query:**
```sql
SELECT *
FROM '{CQ_DATASET}'
WHERE cq_id = 'cq8';
```

**Output format** -- render as a structured card with four sections:

**Section 1: Header**
```
## cq8: ARID1A Synthetic Lethality

**Question**: How can we identify therapeutic strategies for ARID1A-deficient
Ovarian Cancer using synthetic lethality?

| Property        | Value                        |
|-----------------|------------------------------|
| Category        | Synthetic Lethality          |
| Disease Area    | Oncology (Ovarian Cancer)    |
| Reasoning Type  | multi_hop_traversal          |
| Complexity      | advanced                     |
| Num Hops        | 4                            |
| Source          | Original                      |
| Group ID        | cq8-arid1a-synthetic-lethality|
```

**Section 2: Key Entities**

Render the `key_entities` list as a table with BioLink types and CURIEs:
```
### Key Entities

| Entity     | CURIE            | BioLink Type           | Role                          |
|------------|------------------|------------------------|-------------------------------|
| ARID1A     | HGNC:11110       | biolink:Gene           | Tumor suppressor (SWI/SNF)    |
| EZH2       | HGNC:3527        | biolink:Gene           | Synthetic lethal partner (PRC2)|
| ATR        | HGNC:882         | biolink:Gene           | Synthetic lethal partner       |
| Tazemetostat| CHEMBL:3414621  | biolink:SmallMolecule  | EZH2 inhibitor (FDA approved) |
| NCT03348631| NCT:03348631     | biolink:ClinicalTrial  | Phase 2 trial                 |
```

CURIE prefixes indicate the source database:
- `HGNC:` -- HUGO Gene Nomenclature Committee
- `CHEMBL:` -- ChEMBL compound database
- `MONDO:` -- Monarch Disease Ontology
- `STRING:` -- STRING protein interaction database
- `NCT:` -- ClinicalTrials.gov
- `WP:` -- WikiPathways
- `ENSG` -- Ensembl gene ID

**Section 3: Gold Standard Path**

Render the `gold_standard_path` as a visual traversal diagram. Parse the path string and display it as an ASCII graph:

```
### Gold Standard Path (4 hops)

  Gene(ARID1A)
       |
       | --[loss_of_function]-->
       v
  GeneFamily(SWI/SNF)
       |
       | --[synthetic_lethal_with]-->
       v
  Gene(EZH2)
       |
       | --[target_of]-->
       v
  Drug(Tazemetostat)
       |
       | --[tested_in]-->
       v
  Trial(NCT03348631)
```

If `biolink_edges` is present, also show the typed edge table:
```
### BioLink Edges

| Source           | Predicate                              | Target           |
|------------------|----------------------------------------|------------------|
| HGNC:11110       | biolink:loss_of_function_contributes_to | MONDO:0005140   |
| HGNC:11110       | biolink:synthetic_lethal_with          | HGNC:3527        |
| HGNC:3527        | biolink:target_of                      | CHEMBL:3414621   |
```

**Section 4: Workflow and Next Steps**

Show the workflow steps as a numbered list:
```
### Workflow Steps

1. Anchor: hgnc_search_genes("ARID1A") -> HGNC:11110
2. Enrich: uniprot_get_protein("UniProtKB:O14497") -> SWI/SNF function
3. Expand: string_get_interactions() -> SWI/SNF complex members
4. Traverse: chembl_search_compounds("tazemetostat") -> CHEMBL:3414621
5. Validate: ChEMBL /mechanism -> EZH2 inhibitor
6. Persist: graphiti add_memory(group_id="cq8-arid1a-synthetic-lethality")
```

Show the APIs used as tags:
```
**APIs**: ChEMBL, HGNC, UniProt, STRING, Open Targets
```

Then offer actionable next steps:
```
### Next Steps

- Run `/ob-cq-run [cq_id]` to execute this CQ against live MCP servers
- Run `/ob-cq-discover` with a filter to find related CQs (e.g., other oncology CQs, other synthetic lethality CQs)
- View the validation report: docs/competency-validations/cq8-arid1a-synthetic-lethality.md
```

## Cross-CQ Analysis Queries

For users who want to understand the CQ catalog as a whole, support these analytical queries:

**API coverage heatmap:**
```sql
-- Which APIs are used most frequently?
SELECT api, COUNT(*) as cq_count
FROM (
    SELECT cq_id, UNNEST(apis_used) as api
    FROM '{CQ_DATASET}'
)
GROUP BY api
ORDER BY cq_count DESC;
```

**Reasoning type distribution:**
```sql
SELECT reasoning_type, COUNT(*) as count,
       LIST(cq_id ORDER BY cq_id) as cq_ids
FROM '{CQ_DATASET}'
GROUP BY reasoning_type
ORDER BY count DESC;
```

**Complexity vs hops:**
```sql
SELECT complexity,
       MIN(num_hops) as min_hops,
       MAX(num_hops) as max_hops,
       ROUND(AVG(num_hops), 1) as avg_hops,
       COUNT(*) as count
FROM '{CQ_DATASET}'
GROUP BY complexity;
```

**Entity type inventory:**
```sql
-- What BioLink types appear across all CQs?
SELECT entity.type as biolink_type, COUNT(*) as count
FROM (
    SELECT UNNEST(key_entities) as entity
    FROM '{CQ_DATASET}'
)
GROUP BY entity.type
ORDER BY count DESC;
```

## Matching User Requests to Modes

| User says... | Mode | Action |
|-------------|------|--------|
| "show me all CQs" | 1 (Summary) | Full table, no filters |
| "list competency questions" | 1 (Summary) | Full table, no filters |
| "what CQs are available?" | 1 (Summary) | Full table, no filters |
| "find CQs about Alzheimer's" | 2 (Filtered) | `disease_area LIKE '%Alzheimer%'` |
| "which CQs use STRING?" | 2 (Filtered) | `list_contains(apis_used, 'STRING')` |
| "show advanced CQs" | 2 (Filtered) | `complexity = 'advanced'` |
| "CQs with 4+ hops" | 2 (Filtered) | `num_hops >= 4` |
| "oncology synthetic lethality CQs" | 2 (Filtered) | `disease_area LIKE '%Oncology%' AND category LIKE '%Synthetic%'` |
| "show me cq8" | 3 (Detail) | Full record for cq8 |
| "details for cq1" | 3 (Detail) | Full record for cq1 |
| "tell me about the FOP mechanism question" | 3 (Detail) | Match by content, then full record |
| "what APIs are most used?" | Analysis | Cross-CQ analysis query |
| "which reasoning types are there?" | Analysis | Reasoning type distribution |

When the user's request is ambiguous (e.g., "CQs for drug discovery"), prefer Mode 2 (Filtered) with a broad filter, then offer to narrow down or show details for any specific CQ.

## Error Handling

**DuckDB not available**: If DuckDB is not installed, instruct the user:
```
DuckDB is required for this skill. Install it with:
  pip install duckdb
or if using uv:
  uv pip install duckdb
```

**Network issues**: If the HuggingFace Hub is unreachable, report the error and suggest:
```
Could not reach HuggingFace Hub. Check your network connection.
The dataset is public at: https://huggingface.co/datasets/open-biosciences/biosciences-competency-questions-sample
```

**No matching CQs**: If a filter returns zero results, show what filters were applied and suggest relaxing them:
```
No CQs match: disease_area LIKE '%Malaria%'

Available disease areas:
  Rare Disease (FOP), Neurodegeneration (Alzheimer's), Oncology (MAPK pathway), ...

Try a broader search or check /ob-cq-discover for the full catalog.
```

## Relationship to Other Skills

| From this skill... | ...you can go to |
|-------------------|------------------|
| Found an interesting CQ | Run `/ob-cq-run [cq_id]` -- execute the CQ against live MCP servers |
| Want to see validation results | Read `docs/competency-validations/[cq_id]-*.md` in biosciences-research |
| Want free-form research | Run `/ob-research [question]` for free-form graph-builder research |
| Want to see the raw dataset | https://huggingface.co/datasets/open-biosciences/biosciences-competency-questions-sample |

## Example Invocations

### Example 1: Browse all CQs
```
User: /ob-cq-discover
User: Show me all competency questions
User: What research questions are in the catalog?
```

### Example 2: Filter by disease
```
User: /ob-cq-discover oncology
User: Find CQs about Alzheimer's disease
User: Which competency questions cover rare diseases?
```

### Example 3: Filter by API
```
User: /ob-cq-discover STRING
User: Which CQs use ClinicalTrials.gov?
User: Find CQs that need both ChEMBL and Open Targets
```

### Example 4: Filter by complexity
```
User: /ob-cq-discover advanced
User: Show me intermediate CQs with 3 or fewer hops
User: What are the simplest competency questions?
```

### Example 5: Detail view
```
User: /ob-cq-discover cq8
User: Tell me about the synthetic lethality question
User: Show details for the Palovarotene mechanism CQ
```

### Example 6: Analysis
```
User: /ob-cq-discover --analysis
User: Which APIs are used most across all CQs?
User: What reasoning types do the CQs cover?
```
