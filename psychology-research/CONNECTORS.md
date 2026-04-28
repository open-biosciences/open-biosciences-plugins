# Connectors

## How Tool References Work

Plugin files use `~~category` placeholders for whatever tool the user connects in that category. For example, `~~literature` might mean PubMed, PsycINFO, Semantic Scholar, Crossref, or another literature source.

The plugin is tool-agnostic. It describes workflows in terms of source categories rather than specific products. If no connected tool can verify a claim, mark the claim `UNRESOLVED` instead of filling the gap from memory.

## Connectors For This Plugin

| Category | Placeholder | Default Binding (Tier-?) | Primary Uses |
|----------|-------------|--------------------------|--------------|
| Literature | `~~literature` | (Tier-2: pubmed, semantic-scholar) | Peer-reviewed psychology, psychiatry, sex therapy, family systems, and psychotherapy research |
| Web search/browser | `~~web` | (always: tier-capped at SUPPORTED) | Current provider pages, professional directories, official organizations, and public practice pages |
| Licensing board | `~~licensing-board` | (Tier-3: per-state adapters) | State license lookup and disciplinary-status verification |
| Certifying body | `~~certifying-body` | (Tier-3: AASECT, ICEEFT, AEDP, SE, EMDRIA, IFS, Gottman, PACT adapters) | AASECT, ICEEFT, AEDP Institute, SE International, EMDRIA, IFS Institute, and similar credential checks |
| Guidelines | `~~clinical-guidelines` | (Tier-4: NICE, VA-CPG, SAMHSA + non-biomedical block) | Professional guidelines, consensus statements, and official clinical resources |
| Local knowledge graph | `~~graph-memory` | (optional, user-configured) | Optional Graphiti/Neo4j persistence or prior evidence-packet retrieval |

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

Within a category, ordering is alphabetical by server name. This ordering is documented here rather than encoded in JSON because JSON has no comments; PR review enforces the convention. Tier-1a ships with `mcpServers: {}`, so the convention is enforced on first population at Tier-2 entry.
