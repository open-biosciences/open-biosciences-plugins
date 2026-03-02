# Bio-Research Plugin

Connect to preclinical research tools and databases (literature search, genomics analysis, target prioritization) to accelerate early-stage life sciences R&D. Use with [Cowork](https://claude.com/product/cowork) or install directly in Claude Code.

This plugin consolidates MCP server integrations, domain-specific biosciences skills, and analysis workflows into a single package for life science researchers.

## What's Included

### MCP Servers (Data Sources & Tools)

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](CONNECTORS.md).

| Provider | What It Does | Category/Placeholder |
|----------|-------------|---------------------|
| Open Biosciences | 34-tool gateway spanning HGNC, UniProt, STRING, BioGRID, ChEMBL, Open Targets, PubChem, IUPHAR, WikiPathways, ClinicalTrials.gov, Ensembl, Entrez | `biosciences-mcp` |
| Sage Bionetworks | Collaborative research data management | `~~data repository` |

### Skills (Analysis & Research Workflows)

#### Biosciences Domain Skills

Nine skills for structured research using life sciences APIs. These follow a LOCATE→RETRIEVE discipline where entities are resolved through search endpoints before strict lookup by canonical ID. See [references/fuzzy-to-fact.md](references/fuzzy-to-fact.md) for details.

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

### Commands

| Command | What It Does |
|---------|-------------|
| `/ob-research` | Run structured research on a competency question — entity resolution, network expansion, drug/trial discovery |
| `/ob-report` | Format findings as a report with evidence grading |
| `/ob-review` | Quality review against 10 evaluation dimensions |
| `/ob-publish` | Generate publication files: report, KG JSON, Synapse grounding, quality review, BioRxiv draft |

## Getting Started

```bash
# Install the plugin
/install open-biosciences/open-biosciences-plugins bio-research

# Run the start command to see available tools
/start
```

## Common Workflows

**Literature Review**
Search ~~literature database for papers, access full-text through ~~journal access, and create figures with ~~scientific illustration.

**Single-Cell Analysis**
Run QC on scRNA-seq data, then use scvi-tools for integration, batch correction, and cell type annotation.

**Sequencing Pipeline**
Download public data from GEO/SRA, run nf-core pipelines (RNA-seq, variant calling, ATAC-seq), and verify outputs.

**Drug Discovery**
Search ~~chemical database for bioactive compounds, use ~~drug targets for target prioritization, and review clinical trial data. For structured multi-database research, try `/ob-research` with a specific question.

**Graph-Based Research**
Ask a competency question with `/ob-research` to resolve entities across databases, build interaction networks, and discover drug candidates and clinical trials. Format results with `/ob-report`, review with `/ob-review`, or generate publication files with `/ob-publish`.

**Research Strategy**
Pitch a new idea, troubleshoot a stuck project, or evaluate strategic decisions using the scientific problem selection framework.

## License

Skills are licensed under Apache 2.0. MCP servers are provided by their respective authors — see individual server documentation for terms.
