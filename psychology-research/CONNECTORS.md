# Connectors

## How Tool References Work

Plugin files use `~~category` placeholders for whatever tool the user connects in that category. For example, `~~literature` might mean PubMed, PsycINFO, Semantic Scholar, Crossref, or another literature source.

The plugin is tool-agnostic. It describes workflows in terms of source categories rather than specific products. If no connected tool can verify a claim, mark the claim `UNRESOLVED` instead of filling the gap from memory.

## Connectors For This Plugin

| Category | Placeholder | Primary Uses |
|----------|-------------|--------------|
| Literature | `~~literature` | Peer-reviewed psychology, psychiatry, sex therapy, family systems, and psychotherapy research |
| Web search/browser | `~~web` | Current provider pages, professional directories, official organizations, and public practice pages |
| Licensing board | `~~licensing board` | State license lookup and disciplinary-status verification |
| Certifying body | `~~certifying body` | AASECT, ICEEFT, AEDP Institute, Somatic Experiencing International, EMDRIA, IFS Institute, and similar credential checks |
| Guidelines | `~~clinical guidelines` | Professional guidelines, consensus statements, and official clinical resources |
| Local knowledge graph | `~~graph memory` | Optional Graphiti/Neo4j persistence or prior evidence packet retrieval |

## Current-Information Rule

Provider availability, licensure, disciplinary status, telehealth jurisdiction, credential status, and contact details are current facts. Verify them live through official or near-official sources when possible, record `retrieved_at`, and downgrade stale or self-reported data to `SELF_REPORTED` or `UNRESOLVED`.

## Safety Rule

This plugin supports research and fit assessment only. It is not therapy, not diagnosis, not a prescription engine, and not a substitute for a licensed clinician. For acute self-harm, suicide risk, or psychiatric crisis, name 988 and pause research analysis.
