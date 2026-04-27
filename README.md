# Open Biosciences Plugins

Connect to structured research workflows, domain-specific skills, and MCP-backed data sources. Use with [Cowork](https://claude.com/product/cowork) or install directly in Claude Code.

This marketplace contains reusable research plugins:

| Plugin | What It Does |
|--------|--------------|
| **bio-research** | Connects to preclinical research tools and databases for life sciences R&D |
| **psychology-research** | Runs evidence-grounded psychology research and therapist/provider fit assessment |

## Bio Research

### MCP Servers (Data Sources & Tools)

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](bio-research/CONNECTORS.md).

| Provider | What It Does | Category/Placeholder |
|----------|-------------|---------------------|
| Open Biosciences | 34-tool gateway spanning HGNC, UniProt, STRING, BioGRID, ChEMBL, Open Targets, PubChem, IUPHAR, WikiPathways, ClinicalTrials.gov, Ensembl, Entrez | `biosciences-mcp` |
| Open Biosciences | Edge tools: ORCS CRISPR essentiality, ChEMBL mechanism-of-action | `biosciences-mcp-edge` |
| Sage Bionetworks | Collaborative research data management | `~~data repository` |

### Skills (Analysis & Research Workflows)

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

## Psychology Research

`psychology-research` adapts the same grounding discipline to psychology, therapy, and provider-fit workflows. It is a Markdown-only v1: commands, skills, and references, with no bundled MCP servers or runtime services.

### Skills

| Skill | What It Does |
|-------|--------------|
| **psychology-evidence-builder** | Builds evidence packets for psychology and therapy research using `LOCATE -> RETRIEVE -> EXTRACT -> CLASSIFY -> SYNTHESIZE` |
| **psychology-provider-fit** | Verifies provider fit, licensure, credentials, modality claims, geography, telehealth, and gaps |
| **psychology-reporting** | Formats sourced reports with evidence labels and safety language |
| **psychology-quality-review** | Reviews reports for source attribution, overclaiming, clinical safety, provider verification, and hallucination risk |

### Commands

| Command | What It Does |
|---------|--------------|
| `/psy-research` | Run evidence-grounded psychology research from a question or document |
| `/psy-provider` | Verify therapist/provider fit, credentials, modality claims, and gaps |
| `/psy-report` | Format a sourced report from an evidence packet |
| `/psy-review` | Quality-review a report and evidence packet |

### Safety

Psychology Research is research support, not therapy, not diagnosis, and not medical advice. It does not diagnose, prescribe, rank a clinician as clinically best, or simulate real clinicians. Crisis/self-harm content routes to 988 and pauses analysis.

### Install

```
/plugin install psychology-research@open-biosciences-plugins
```

## License

Skills are licensed under Apache 2.0. MCP servers are provided by their respective authors — see individual server documentation for terms.
