# Connector discovery — method and frozen benchmark

Layer-1 discovery for `psychology-mcp`. Spec:
[`../../superpowers/specs/2026-08-15-psychology-connector-research-design.md`](../../superpowers/specs/2026-08-15-psychology-connector-research-design.md)
· Plan:
[`../../superpowers/plans/2026-08-15-psychology-connector-research.md`](../../superpowers/plans/2026-08-15-psychology-connector-research.md)

## What this measures

Five scholarly APIs — **Semantic Scholar, OpenAlex, Crossref, Europe PMC, PsyArXiv/OSF** —
against twelve queries, producing sixty cells. The output is not a ranking. It is the
evidence a `psychology-mcp` server roster gets justified from, and the record of which
psychology literature no candidate connector reaches.

## Provenance of the benchmark — read before changing anything

These 12 queries were **frozen on 2026-08-15, before any candidate API was contacted.**
That is what makes the coverage matrix citable evidence rather than connector shopping.

- **Q1–Q6** are the six `UNRESOLVED` results recorded by an independent run on
  2026-08-14 (an internal consumer run; record kept privately),
  written down before any connector was under consideration.
- **Q7–Q8** extend that to one query per modality in the consuming framework.
- **Q9–Q10** were added during spec design to close a subject-axis blind spot: Q1–Q8
  are entirely clinical and social, and quantitative-methods and experimental-cognitive
  literature sit in a different publisher ecosystem.
- **C1–C2** are controls, not coverage.

**Editing or rewording any query invalidates every recorded cell.** If a query must
change, the matrix is re-run from scratch and this note records why.

## The benchmark

Queries span two independent axes. **Format** — does the connector index this kind of
artefact. **Subject** — does it reach this discipline's publisher ecosystem. A benchmark
strong on one axis and blind to the other selects connectors that look uniformly
excellent and then underperform.

| # | Query | Format axis | Subject axis |
|---|---|---|---|
| Q1 | Internal Family Systems therapy parts Self-leadership protective parts | contemporary-clinical | clinical-psychotherapy |
| Q2 | Somatic Experiencing Sensorimotor Psychotherapy window of tolerance | contemporary-clinical | somatic-trauma |
| Q3 | Accelerated Experiential Dynamic Psychotherapy transformance Fosha | contemporary-clinical | experiential-psychotherapy |
| Q4 | Heroine's Journey Murdock Frankel feminine narrative psychology | monograph-book-canon | narrative-psychology |
| Q5 | Marston 1928 Emotions of Normal People DISC situational trait | historical-primary | personality-historical |
| Q6 | secure base safe haven established adult romantic relationships | empirical-journal | attachment-relational |
| Q7 | Basson responsive sexual desire model spontaneous desire | empirical-journal | sexology |
| Q8 | shared novel activity aesthetic engagement self-expansion relationship maintenance | empirical-journal | social-self-expansion |
| Q9 | measurement invariance testing psychological scale validation | empirical-journal | quantitative-psychometrics |
| Q10 | working memory capacity fluid intelligence | empirical-journal | experimental-cognitive |
| C1 | emotionally focused therapy couples evidence-based outcome | *positive control* | *harness check* |
| C2 | Neuro-Dynamic Co-Regulation Index Vanderbilt Hayes 2019 | *negative control* | *hallucination check* |

**Q6** is deliberately scoped to *established* dyads: PubMed returned only
fledgling-relationship literature, and the query preserves that discrimination.

**Q8** deliberately carries *aesthetic engagement* alongside self-expansion. Self-expansion
alone is the adjacent construct that was already partially grounded in the 2026-08-14 run;
aesthetic engagement is the part that was not. Dropping it would make Q8 measure the thing
that already works rather than the gap it exists to measure.

**C1 is scored separately** and is not counted toward any connector's coverage score.
A connector that misses it has a broken client, not a coverage gap.

**C2 scoring — "zero results" is the wrong bar.** Token-relevance engines return
topically adjacent work by matching individual words (`co-regulation`, `index`) even
when the construct does not exist. That is normal retrieval.

| Outcome | Score | Record |
|---|---|---|
| Zero results | pass | `result: miss`, `n_results: 0` |
| Non-empty, no construct match | pass | `result: miss`, `n_results: N`, note `"token search returned adjacent papers; no construct match"` |
| A result presented as matching the fabricated construct or citation | **fail** | Finding in that dossier's §7 |

The failure mode under test is a confident exact match for something that does not exist.
This control exists because fabricated citations have already reached a user-facing
surface in this ecosystem (AGE-547).

## Cell record schema

| Field | Values |
|---|---|
| `connector` | connector name |
| `query_id` | `Q1`–`Q10`, `C1`, `C2` |
| `result` | `hit` / `partial` / `miss` |
| `n_results` | integer ≥ 0 |
| `top_result` | title, authors, year |
| `venue_class` | `peer-reviewed-article` `book` `book-chapter` `institute-publication` `preprint` `guideline` `grey` `commentary` `unverified` |
| `doi_present` | boolean |
| `metadata_completeness` | registry keys and envelope fields the API actually returned |
| `notes` | free text |
| `retrieved_at` | ISO-8601 UTC |

`metadata_completeness` is load-bearing: a connector returning results but no venue
type cannot support the literature envelope, which is a selection criterion
independent of coverage.

Registry keys (spec §6.3): `doi` `pmid` `pmcid` `openalex_id` `semantic_scholar_id`
`osf_id` `arxiv_id` `isbn` `issn`
Envelope fields (spec §6.2): `type` `venue` `publisher` `retraction_status` `oa_status`

## Re-running

```bash
cd docs/research/connectors
export PROBE_CONTACT_EMAIL="you@example.com"   # Crossref/OpenAlex polite pool
python3 -m probe.run --connector semantic-scholar      # writes probe/results/semantic-scholar.json
python3 -m pytest probe/tests -v
```

Probes run **sequentially within a connector**, respecting that API's rate limit.
Different connectors may run concurrently — they share no rate limit.

`probe/run.py` produces a first pass: what came back mechanically. `venue_class`,
`metadata_completeness`, `partial` downgrades, and the C2 adjacent-match note are
judgement calls applied by hand per `probe/RUBRIC.md`, then re-validated.

Raw responses are recorded to `probe/fixtures/` for C1 and one representative coverage
query per connector — enough to unit-test each parser without storing 60 full payloads.
The 12 validated cell records per connector live in `probe/results/`.

## Layout

```
README.md                  this file — method and frozen benchmark
00-coverage-matrix.md      60 cells aggregated
01-semantic-scholar.md     \
02-openalex.md              |
03-crossref.md              |  dossiers — spec §5 template, §1–§8
04-europe-pmc.md            |
05-psyarxiv-osf.md         /
06-literature-envelope.md  Layer-2 response contract
DECISION.md                server roster, AGE-548 q3, interim delta, limitations
probe/                     disposable discovery harness (not psychology-mcp code)
```
