# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~literature` might mean PubMed, bioRxiv, or any other literature source with an MCP server.

Plugins are **tool-agnostic** — they describe workflows in terms of categories (literature, clinical trials, chemical database, etc.) rather than specific products. The `.mcp.json` pre-configures specific MCP servers, but any MCP server in that category works.

The `biosciences-mcp` gateway is an exception — it provides a unified API across 12 life sciences databases (HGNC, UniProt, STRING, BioGRID, ChEMBL, Open Targets, PubChem, IUPHAR, WikiPathways, ClinicalTrials.gov, Ensembl, Entrez) and is referenced by name rather than by placeholder. The `biosciences-mcp-edge` server extends the gateway with additional tools (ORCS CRISPR essentiality, ChEMBL mechanism-of-action) and is also referenced by name. The biosciences domain skills use these servers alongside the partner connectors listed below.

Skills name these servers' tools as `ServerName:tool_name`, for example `biosciences-mcp:hgnc_search_genes`. Claude Code's full tool name depends on which configuration provides the server: `mcp__plugin_bio-research_<server>__<tool>` when this plugin does, or `mcp__<server-key>__<tool>` when a user, project or local entry for the same URL takes precedence. Match on `<tool>`.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|----------|-------------|-----------------|---------------|
| Literature | `~~literature` | PubMed, bioRxiv | Google Scholar, Semantic Scholar |
| Data repository | `~~data repository` | Synapse | Zenodo, Dryad, Figshare |

