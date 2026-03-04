# Open Biosciences Research Plugin

Connect to preclinical research tools and databases (literature search, genomics analysis, target prioritization) to accelerate early-stage life sciences R&D. Use with [Cowork](https://claude.com/product/cowork) or install directly in Claude Code.

This plugin consolidates MCP server integrations, domain-specific biosciences skills, and analysis workflows into a single package for life science researchers.

## What's Included

### MCP Servers (Data Sources & Tools)

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](bio-research/CONNECTORS.md).

| Provider | What It Does | Category/Placeholder |
|----------|-------------|---------------------|
| Open Biosciences | 34-tool gateway spanning HGNC, UniProt, STRING, BioGRID, ChEMBL, Open Targets, PubChem, IUPHAR, WikiPathways, ClinicalTrials.gov, Ensembl, Entrez | `biosciences-mcp` |
| Open Biosciences | Edge tools: ORCS CRISPR essentiality, ChEMBL mechanism-of-action | `biosciences-mcp-edge` |
| Sage Bionetworks | Collaborative research data management | `~~data repository` |

### Skills (Analysis & Research Workflows)

#### Biosciences Domain Skills

Eleven skills for structured research using life sciences APIs (9 core + 2 beta competency-question skills). These follow a LOCATE→RETRIEVE discipline where entities are resolved through search endpoints before strict lookup by canonical ID. See [bio-research/references/fuzzy-to-fact.md](bio-research/references/fuzzy-to-fact.md) for details.

| Skill | What It Does |
|-------|-------------|
| **biosciences-genomics** | Gene resolution via HGNC, Ensembl, NCBI Entrez |
| **biosciences-proteomics** | Protein interactions via UniProt, STRING, BioGRID |
| **biosciences-pharmacology** | Drug discovery via ChEMBL, PubChem, IUPHAR, Open Targets |
| **biosciences-clinical** | Disease associations and trial discovery via Open Targets, ClinicalTrials.gov |
| **biosciences-crispr** | CRISPR essentiality screen validation via BioGRID ORCS |
| **biosciences-graph-builder** | Orchestrates entity resolution, network expansion, and knowledge graph construction |
| **biosciences-reporting** | Template-based report formatting with evidence grading |
| **biosciences-reporting-quality-review** | 10-dimension quality assessment for reports |
| **biosciences-publication-pipeline** | Publication outputs: report, KG JSON, Synapse grounding, quality review, BioRxiv draft |
| **biosciences-cq-discover** | (beta) Discover and review competency questions from Hugging Face datasets |
| **biosciences-cq-runner** | (beta) Execute competency question research and validation pipelines |

### Commands

| Command | What It Does |
|---------|-------------|
| `/ob-research` | Run structured research on a competency question — entity resolution, network expansion, drug/trial discovery |
| `/ob-report` | Format findings as a report with evidence grading |
| `/ob-review` | Quality review against 10 evaluation dimensions |
| `/ob-publish` | Generate publication files: report, KG JSON, Synapse grounding, quality review, BioRxiv draft |
| `/ob-cq-discover` | (beta) Review competency questions in Hugging Face `open-biosciences` community |
| `/ob-cq-run` | (beta) Wrapper to do competency question driven research and validation |

## Getting Started

```
# Add the marketplace
/plugin marketplace add open-biosciences/open-biosciences-plugins

# Install the plugin
/plugin install bio-research@open-biosciences-plugins
```

## Common Workflows

**Graph-Based Research**
Ask a competency question with `/ob-research` to resolve entities across databases, build interaction networks, and discover drug candidates and clinical trials. Format results with `/ob-report`, review with `/ob-review`, or generate publication files with `/ob-publish`.

## License

Skills are licensed under Apache 2.0. MCP servers are provided by their respective authors — see individual server documentation for terms.
