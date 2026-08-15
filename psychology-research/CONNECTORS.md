# Connectors

## How Tool References Work

Plugin files use `~~category` placeholders for whatever tool the user connects in that category. For example, `~~literature` might mean PubMed, PsycINFO, Semantic Scholar, Crossref, or another literature source.

The plugin is tool-agnostic. It describes workflows in terms of source categories rather than specific products. If no connected tool can verify a claim, mark the claim `UNRESOLVED` instead of filling the gap from memory.

## Connectors For This Plugin

| Category | Placeholder | Default Binding (Tier-?) | Primary Uses |
|----------|-------------|--------------------------|--------------|
| Literature | `~~literature` | **`pubmed`** (declared in `.mcp.json`) | Biomedical, psychiatric and RCT-shaped research **only** — see "What is bound today" below |
| Web search/browser | `~~web` | (always: tier-capped at SUPPORTED) | Current provider pages, professional directories, official organizations, and public practice pages |
| Licensing board | `~~licensing-board` | (Tier-3: per-state adapters) | State license lookup and disciplinary-status verification |
| Certifying body | `~~certifying-body` | (Tier-3: AASECT, ICEEFT, AEDP, SE, EMDRIA, IFS, Gottman, PACT adapters) | AASECT, ICEEFT, AEDP Institute, SE International, EMDRIA, IFS Institute, and similar credential checks |
| Guidelines | `~~clinical-guidelines` | (Tier-4: NICE, VA-CPG, SAMHSA + non-biomedical block) | Professional guidelines, consensus statements, and official clinical resources |
| Local knowledge graph | `~~graph-memory` | (optional, user-configured) | Optional Graphiti/Neo4j persistence, prior evidence-packet retrieval, or a `local_context` graph fragment file (see `references/graph-memory-contract.md`) |

### Graph-memory fragment input

A `~~graph-memory` source may supply context as a **fragment file** — a JSON document
conforming to `references/graph-memory-contract.md`. Its entries enter the evidence packet
as `source_tier: local_context` and can never be labeled `VERIFIED`: a graph-sourced claim
is context local to this effort, not external evidence. Validate a fragment file with
`scripts/validators/graph_memory_fragment.py` before ingestion.

## Current-Information Rule

Provider availability, licensure, disciplinary status, telehealth jurisdiction, credential status, and contact details are current facts. Verify them live through official or near-official sources when possible, record `retrieved_at`, and downgrade stale or self-reported data to `SELF_REPORTED` or `UNRESOLVED`.

## Safety Rule

This plugin supports research and fit assessment only. It is not therapy, not diagnosis, not a prescription engine, and not a substitute for a licensed clinician. For acute self-harm, suicide risk, or psychiatric crisis, name 988 and pause research analysis.

## .mcp.json category ordering

When `mcpServers` entries are populated (Tier-2 onward), they are ordered by category in the file:

1. Literature servers
2. Certifying-body servers
3. Licensing-board servers
4. Clinical-guidelines servers

Within a category, ordering is alphabetical by server name. This ordering is documented here rather than encoded in JSON because JSON has no comments; PR review enforces the convention.

Every entry **must** carry `"type": "http"`. An entry with a `url` and no `type` is read as a stdio server, skipped at load, and warned about.

## What is bound today, and what is not

`.mcp.json` declares **one** server:

```json
{ "mcpServers": { "pubmed": { "type": "http", "url": "https://pubmed.mcp.claude.com/mcp" } } }
```

**This closes the biomedical half of the literature category and nothing else.** PubMed's own scope note excludes non-medical psychology. A 2026-08-14 consumer run with PubMed bound still returned `UNRESOLVED` for IFS, Somatic Experiencing / Sensorimotor, AEDP transformance, the Heroine's Journey, Marston DISC, and secure-base research in established adult dyads.

Claims in those paradigms fall through to `~~web` and stay tier-capped at `SUPPORTED`. **Say so in the report** rather than presenting a PubMed miss as evidence of absence.

### What closes the rest

A Layer-1 discovery pass measured five candidate APIs against a frozen 12-query benchmark (49 recorded cells). Result:

| Connector | Coverage | Roster position |
|---|---|---|
| **Crossref** | 8 hit / 2 partial / 0 miss | **Tier 0** — the only connector reaching book canon and historical primaries; sole source of `isbn` and registered `type` |
| **OpenAlex** | 2 / 5 / 3 | **Tier 0** — the only source of standing retraction status |
| Europe PMC | 2 / 2 / 6 | Tier 1 — sole source of `pmcid`; missed the modality queries entirely |
| Semantic Scholar | *not measured* | Tier 2 — unauthenticated API returns sustained HTTP 429; needs a key |
| PsyArXiv / OSF | 0 / 0 / 10 | not scheduled — `filter[title]` is a substring match, not an index |
| APA PsycNET | — | **removed** — no query API at any access level (SPA shell, `robots.txt` disallow, TDM rights reserved) |

These arrive as first-party servers in **`psychology-mcp`**, the platform's Layer-2 gateway for psychology — the counterpart to `biosciences-mcp`, which `bio-research` declares. Until it is deployed, this plugin's literature reach is the single PubMed binding above.

Full evidence, including the per-connector dossiers and the response-envelope design: `docs/research/connectors/` in this repository.
