# OpenAlex — connector dossier

Probe artifacts: `probe/connectors/openalex.py` · `probe/tests/test_openalex.py` ·
`probe/fixtures/openalex-C1.json` · `probe/results/openalex.json`

All 12 cells were fetched from the live `api.openalex.org` API on 2026-08-15
(retrieved_at `2026-08-15T21:11:17Z`). No results were extrapolated or invented;
every cell in `probe/results/openalex.json` traces to an actual HTTP response, and
top results were independently re-fetched and cross-checked (same top hit both times)
before hand-classification. Total real HTTP calls made against `api.openalex.org`
during this task: **39** — 1 fixture capture, 12 for the recorded run
(`python3 -m probe.run --connector openalex`), 12 detail re-fetches (via `search()`) to
inspect `type`/`venue`/`publisher`/`retraction_status`/`oa_status` for hand
classification, 12 raw-payload re-fetches to enumerate exactly which `ids.*` keys were
present per record, and 2 supplementary checks (`select=` slim fields, `cursor=*`
pagination) for §6. None were throttled; no 429 was observed at `RATE = 0.15`s
(≈6.7 req/s, well under the polite-pool ceiling), so `RATE` was not raised.

## 1. Identity and access

- **Base URL:** `https://api.openalex.org/works` (this dossier covers the `works`
  entity only, per the benchmark's literature scope).
- **Auth model:** Keyless. Confirmed live — every one of the 39 calls above
  succeeded with no key, using only `mailto=` for polite-pool identification.
- **Rate limits (current, per `ourresearch/openalex-docs` `rate-limits-and-authentication.md`,
  fetched 2026-08-15):** free/unkeyed tier is **100,000 credits/day**, **max 100
  requests/second**. Users are split into a **common pool** and a **polite pool**;
  the polite pool (more consistent response times) is entered by adding
  `mailto=you@example.com` as a query param or `mailto:you@example.com` in the
  `User-Agent` header — exactly the mechanism this probe uses
  (`PROBE_CONTACT_EMAIL` → `probe.connectors.base.USER_AGENT` and this adapter's
  `mailto` param). An API key exists only for a premium tier (higher credits +
  extra filters); it is not required for the free tier.
  **Caveat:** one web-search snippet claimed OpenAlex would require API keys and
  discontinue the polite pool starting 2026-02-13. The current primary-source docs
  (fetched directly, not from a cache) contradict this — "You don't need an API key
  to use OpenAlex" — and our own live keyless+mailto calls on 2026-08-15 (six months
  past that claimed date) succeeded without a key. Recorded as an unconfirmed claim
  contradicted by direct verification, not as fact.
- **ToS / attribution:** OpenAlex data is CC0 (public domain dedication); the docs
  ask only for the polite-pool `mailto` courtesy above, not a display-attribution
  requirement. No DOI-link attribution obligation was observed (unlike the PubMed
  connector, which the plan flags as a precedent for non-trivial attribution
  requirements) — nothing in the fetched docs imposes one for `works` lookups.

## 2. Mechanics

- **Request/response format:** plain HTTP GET, JSON response. `search=` performs a
  **full-text token match** (confirmed via the response's own `meta.x_query.oql`:
  `works where full text has (...)`) — not a ranked bibliographic-relevance search
  restricted to title/abstract. This is the direct cause of several topically
  unrelated top hits in §4 (Q1, Q4, Q8): the token search matches anywhere in
  full text, so a paper containing the query's words in an unrelated context can
  out-rank the actually relevant work. `results` are still returned in a
  `relevance_score`-descending order, but relevance is computed over a much larger
  surface than title/abstract.
- **Pagination:** two independent models, both confirmed live —
  - **Offset (`page`)**: `meta.page`/`meta.per_page` returned; usable up to
    10,000 results deep (OpenAlex's documented cap on basic pagination).
  - **Cursor (`cursor=*` then `meta.next_cursor`)**: confirmed live — a request with
    `cursor=*` returns `meta.page: null` and a `meta.next_cursor` token for the next
    page, walking arbitrarily deep result sets. Not used by this adapter (`search()`
    takes only `limit`), but available for a Layer-2 server needing full-corpus
    walks.
- **Filtering:** a full `filter=` query language exists (field:value, ANDed via
  commas) beyond what this probe exercises; not tested here.
- **Slim/field selection:** `select=id,doi,title,type,primary_location` was
  confirmed live to return only the requested top-level fields — this is a real,
  working slim mechanism (relevant to §6.4's slim-mode requirement, see §6 below).
- **Batch:** no multi-ID batch-fetch endpoint for `works` was exercised; `filter=`
  supports OR-lists of IDs (`openalex_id:W1|W2|...`) per OpenAlex's general filter
  syntax, which is the closest analog to a batch call, but this was not verified
  live in this pass.
- **Error behaviour:** not exercised — all 39 calls in this pass returned HTTP 200;
  no malformed-query or invalid-ID call was made to observe OpenAlex's error shape.

## 3. Item metadata

Mapped against the Literature Key Registry (spec §6.3) and envelope fields (§6.2),
as **actually observed** in the raw JSON for the 12 top results (not from OpenAlex's
documentation — see RUBRIC.md's "what the API actually returned").

| Registry/envelope field | Observed | Source path |
|---|---|---|
| `doi` | present for 11/12 (absent for Q3, an institutional-repository record) | `results[].doi` (a full `https://doi.org/10.x` URL — the adapter normalises to bare `10.x`) |
| `pmid` | present for 6/12 (Q1, Q2, Q6, Q7, Q10, C1) | `results[].ids.pmid` |
| `pmcid` | **not observed** in any of the 12 records | `results[].ids.pmcid` — the key was simply absent, never present-but-null |
| `openalex_id` | present 12/12 | `results[].id` |
| `semantic_scholar_id`, `osf_id`, `arxiv_id`, `isbn` | not observed | OpenAlex does not appear to surface these identifiers on `works` records in this sample |
| `issn` | present for 11/12 (absent for Q3 — a repository, not a journal) | `results[].primary_location.source.issn` — **note:** this is the venue's ISSN, not a per-work identifier; it cross-references the container, same status as `venue`/`publisher` below |
| `type` (envelope) | present 12/12 | `results[].type` |
| `venue` (envelope) | present 12/12 | `results[].primary_location.source.display_name` |
| `publisher` (envelope) | present 12/12 | `results[].primary_location.source.host_organization_name` |
| `retraction_status` (envelope) | present 12/12, **always as an explicit boolean** | `results[].is_retracted` — see finding below |
| `oa_status` (envelope) | present 12/12 | `results[].open_access.oa_status` |

**`is_retracted` finding (spec §10 open question 3):** across all 12 top results
`is_retracted` was present and explicitly `false` — not absent, not null. OpenAlex
appears to always populate this field with a boolean rather than omitting it when
unknown, which makes it a reliable, first-class retraction signal **without a second
Crossref lookup**. This dossier did not encounter a retracted work to confirm the
`true` case, so "OpenAlex flags retraction inline" is confirmed for the negative case
(12/12) but the positive case is untested in this pass — a real limitation to flag,
not a reason to withhold the finding.

**Distinct `type` values observed** (top result, all 12 queries):

| `type` | Count | Queries |
|---|---|---|
| `article` | 11 | Q1, Q2, Q3, Q4, Q6, Q7, Q8, Q9, Q10, C1, C2 |
| `conference-paper` | 1 | Q5 |

This is a narrow slice — only the top-1 result of 12 queries — and undersells
OpenAlex's real type vocabulary. A single supplementary (non-benchmark) call made
for this section, `search=emotionally focused therapy couples`, surfaced
`type: "book"` (*The Practice of Emotionally Focused Couple Therapy: Creating
Connection*, `doi: null`) at rank 1 — confirming `book` is a live value in the
vocabulary even though it never appeared in the frozen 12. Not counted as a 13th
coverage cell; recorded here only to avoid overclaiming "OpenAlex mostly returns
`article`" from an n=12 top-1 sample.

**Adapter gap, noted for the Layer-2 build:** the probe adapter (per the plan's
Task 4 spec) captures `doi`, `type`, `venue`, `publisher`, `retraction_status`,
`oa_status`, and `openalex_id` into `Item`, but **not** `pmid` or `issn`, even
though both are present in the raw payload (table above). This is correct for a
disposable probe scoped to the 12-cell benchmark; a real `psychology-mcp` server
implementing the literature Key Registry's `cross_references` object (ADR-001 §4)
would need to add both.

## 4. Measured coverage

| Query | Result | n_results | venue_class | Example (top result) |
|---|---|---|---|---|
| Q1 IFS therapy | **miss** | 10,134 | peer-reviewed-article | *Health systems resilience in managing the COVID-19 pandemic* — Haldane et al., 2021, *Nature Medicine* — unrelated (full-text token overlap only) |
| Q2 Somatic Experiencing / window of tolerance | **partial** | 600 | peer-reviewed-article | *The brain-body disconnect: A somatic sensory basis for trauma-related disorders* — Kearney & Lanius, 2022, *Frontiers in Neuroscience* — right subject axis, wrong specific modality |
| Q3 AEDP / Fosha / transformance | **partial** | 122 | unverified (no DOI) | *Research on Humanistic-Experiential Psychotherapies* — Elliott, Greenberg & Watson, 2013, Strathprints repository — plausible family match, unconfirmed specificity |
| Q4 Heroine's Journey / Murdock / Frankel | **miss** | 7 | peer-reviewed-article | *Heroine's Learning Journey: Motivating Women in STEM* — Coimbra Costa et al., 2024, *IEEE Access* — metaphor reuse, wrong literature |
| Q5 Marston 1928 / DISC | **partial** | 66 | grey | *Organization of structured interaction … DISC* — Chigova et al., 2019, IOP Conf. Series — right construct, wrong (non-historical) literature |
| Q6 secure base / safe haven, established dyads | **partial** | 5,014 | peer-reviewed-article | *Interdependence, Interaction, and Relationships* — Rusbult & Van Lange, 2002, *Annual Review of Psychology* — adjacent relationship science, not attachment-specific |
| Q7 Basson responsive desire | **hit** | 260 | peer-reviewed-article | *The Female Sexual Response: A Different Model* — Basson, 2000, *J. Sex & Marital Therapy* — exact author/construct match |
| Q8 aesthetic engagement / self-expansion | **miss** | 8,032 | peer-reviewed-article | *Aesthetic and spiritual values of ecosystems* — Cooper et al., 2016, *Ecosystem Services* — wrong field entirely |
| Q9 measurement invariance / scale validation | **partial** | 53,884 | peer-reviewed-article | *The CES-D Scale* — Radloff, 1977, *Applied Psychological Measurement* — scale-validation adjacent, not invariance-testing specific |
| Q10 working memory / fluid intelligence | **hit** | 53,266 | peer-reviewed-article | *The role of prefrontal cortex in working-memory capacity…* — Kane & Engle, 2002, *Psychonomic Bulletin & Review* — exact match |
| C1 EFT couples (positive control) | **hit** | 39,257 | peer-reviewed-article | *A Review of the Research in Emotionally Focused Therapy for Couples* — Wiebe & Johnson, 2016, *Family Process* — exact match, control passes |
| C2 fabricated construct (negative control) | **miss** | 11 | peer-reviewed-article | *Exploring the promising potential of induced pluripotent stem cells in cancer research and therapy* — Chehelgerdi et al., 2023 — unrelated (iPSC/cancer biology); no fabricated-construct false-positive, control passes cleanly |

**Coverage tally (Q1–Q10 only, C1/C2 excluded per README §"C1 is scored separately"):**
2 hit / 6 partial / 2 miss.

**Reading the misses:** all three coverage misses (Q1, Q4, Q8) share the same
mechanism — `search=` is a full-text token match (§2), so a long multi-concept
query string can surface a paper that happens to contain several of the words in
an unrelated context, ranked above (or in the absence of) anything on-construct.
This is a search-quality finding about the `works?search=` endpoint specifically,
not evidence that OpenAlex's corpus lacks this literature — Q7's and C1's hits
show the corpus itself reaches contemporary clinical/relational psychology
without difficulty when the query terms are less ambiguous.

## 5. Fuzzy-to-Fact feasibility (ADR-001 §3)

- **`search_works(query)` → ranked candidates:** yes, directly — `works?search=`
  returns a relevance-ordered list (`relevance_score` descending), exactly the
  Phase-1 fuzzy shape. §4's misses show the ranking quality is uneven for
  multi-concept natural-language queries (full-text token match, not a
  bibliographic relevance model), which is a quality caveat on the ranking, not a
  capability gap.
- **`get_work(doi)` strict lookup:** yes. OpenAlex resolves a DOI directly:
  `GET /works/doi:{doi}` (e.g. `/works/doi:10.1111/famp.12229`) returns the single
  matching work with no ambiguity — not exercised live in this pass (out of the
  12-cell scope) but this is documented, standard OpenAlex behaviour and the DOI
  is exactly the identifier already captured bare-form by this adapter (§1's
  `_bare_doi`). A raw, unresolved string passed to this endpoint would 404 rather
  than partial-match, which maps cleanly to ADR-001 §3's `UNRESOLVED_ENTITY`
  contract for a Layer-2 wrapper to implement.
- **The DOI is the CURIE**, exactly as ADR-001 §3's adaptation note anticipates —
  no additional identifier-resolution layer is needed between Phase 1 and Phase 2
  for OpenAlex specifically.

## 6. FastMCP wrapping feasibility (ADR-001 §2, §7)

- **Async-native REST:** yes — plain HTTP GET/JSON, no vendor SDK, no session
  state. A `psychology-mcp` server would wrap this with strict `httpx.AsyncClient`
  calls per ADR-001 §2's mandate; no `run_in_executor` exception applies (there is
  no legacy sync SDK to wrap).
- **Batch support:** no dedicated multi-ID batch endpoint for `works` was
  confirmed live; the closest mechanism is `filter=openalex_id:ID1|ID2|...`
  (OR-list filtering), not independently verified in this pass. A Layer-2
  implementation should verify this specifically before relying on it for
  fan-out reduction.
- **Cursor support:** confirmed live (§2) — `cursor=*` + `meta.next_cursor` walks
  result sets past the 10,000-row offset-pagination cap, which matters for any
  Layer-2 tool that needs exhaustive rather than top-N retrieval.
- **Rate limits under agent concurrency:** 100 req/s free-tier ceiling (§1) is
  generous relative to what a single-agent MCP tool call pattern would generate;
  the polite-pool `mailto` mechanism this probe already uses is the same
  mechanism a deployed server would use, no separate provisioning needed.
- **Slim mode expressible via `select`:** yes, confirmed live (§2) —
  `select=id,doi,title,type` returns exactly those top-level fields and nothing
  else, a direct, working implementation path for ADR-001 §7's `slim=True`
  requirement and this spec's §6.4 `doi`/`title`/`venue_class` slim triple (the
  first two map directly to `select` fields; `venue_class` is server-computed
  from `type`/`primary_location.source`, not returned as-is by OpenAlex, exactly
  as spec §6.2's resolution order describes).

## 7. Existing MCP server

No first-party MCP server from OpenAlex/OurResearch was found. Multiple
independent, community-maintained servers exist (web search, 2026-08-15):

| Repository | Notes |
|---|---|
| `cyanheads/openalex-mcp-server` | Most substantial of those checked: 119 commits, Apache-2.0, TypeScript, stdio/HTTP/Docker deployment options, changelog to v0.7.8, 6 open issues, a hosted instance. `OPENALEX_API_KEY` explicitly **optional** — anonymous access supported (matches this dossier's own keyless findings in §1). ~11 stars — small but appears actively maintained, not abandoned. |
| `reetp14/openalex-mcp` | Works/Authors/Sources/Institutions tool coverage with ORCID/ROR matching. |
| `drAbreu/alex-mcp` | Scoped specifically to author disambiguation, not general literature search. |
| `oksure/openalex-research-mcp` | General search + citation/collaboration-network analysis framing. |
| `benedict2310/Scientific-Papers-MCP` | Covers arXiv **and** OpenAlex — broader scope than a single-connector server. |

None of these is affiliated with OpenAlex/OurResearch itself, none appears in the
official `modelcontextprotocol/servers` reference repository, and none was load-
tested or auth-verified live in this pass (name, stars, license, and stated
key-optionality only — verified by web fetch, not by calling the server). This is
a **maintainer-risk, not a capability gap**: the underlying OpenAlex REST API is
directly and easily wrappable in-house (§6), so binding to a small, third-party,
single-digit-star community server would trade a well-documented, stable, keyless
REST API for an unaffiliated maintainer's uptime and security posture, for a
connector this project will call frequently.

## 8. Recommendation: **wrap** in `psychology-mcp`

**Reasoning:**
- Keyless, generous rate limits (§1), no attribution/ToS burden beyond a polite
  `mailto` (§1) — the lowest-friction of the identity/access profiles checked so
  far in this program.
- Directly satisfies both ADR-001 §3 (Fuzzy-to-Fact: `search=` for ranked
  candidates, DOI-keyed strict lookup) and §7 (token budgeting: confirmed working
  `select=` slim mode, cursor pagination for exhaustive walks) with no
  adaptation gymnastics (§5, §6).
- `is_retracted` is present and reliably boolean on every record observed (§3) —
  this is the strongest, lowest-cost retraction signal found in this connector
  and answers spec §10 open question 3 for the negative case: **no second
  Crossref lookup is needed to know a work is *not* retracted.** (The positive
  case — a genuinely retracted work — was not encountered in this 12-query
  sample and remains unconfirmed; flagged, not assumed.)
- No credible existing MCP server to bind instead (§7) — the community options
  are small, unaffiliated, and not more capable than an in-house wrapper would
  be over an API this simple to call directly.

**Residual risks:**
1. **`search=` full-text token matching produces poor precision on long,
   multi-concept natural-language queries** (§2, §4) — 3 of 10 coverage queries
   missed entirely because of word-overlap-driven false ranking, not corpus
   absence. A Layer-2 `search_works` tool wrapping this endpoint should not be
   assumed to behave like a bibliographic-relevance search; downstream consumers
   (or the server itself) may need query reformulation or a secondary filter
   pass to improve precision.
2. **Batch fetch is unverified** (§6) — before relying on `filter=id:A|B|...`
   for fan-out reduction in the Layer-2 build, confirm it live; this dossier
   did not exercise it.
3. **The claimed 2026-02-13 mandatory-API-key change is unconfirmed and
   contradicted by both the current primary-source docs and this dossier's own
   live keyless calls** (§1) — worth one direct re-check at Layer-2 build time
   in case OpenAlex's policy shifts again between now and then.
4. **`pmcid`/`semantic_scholar_id`/`osf_id`/`arxiv_id`/`isbn` were never observed**
   (§3) — OpenAlex is not a cross-reference completeness play; triangulation
   (ADR-001 §6) against those identifiers will depend on the *other* four
   connectors in this program, not on OpenAlex supplying them.
