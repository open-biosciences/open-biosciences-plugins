# Europe PMC

Dossier for `psychology-mcp` Layer-1 discovery. Method, frozen benchmark, and cell
schema: [`README.md`](README.md). Classification rubric applied throughout:
[`probe/RUBRIC.md`](probe/RUBRIC.md). Spec:
[`../../superpowers/specs/2026-08-15-psychology-connector-research-design.md`](../../superpowers/specs/2026-08-15-psychology-connector-research-design.md)
§5 (dossier template), §6 (literature envelope), §10 q1 (supersede-vs-complement).

Adapter: `probe/connectors/europe_pmc.py`. Tests: `probe/tests/test_europe_pmc.py`
(7 tests, pass). Fixture: `probe/fixtures/europe-pmc-C1.json` (real recorded
response, `hitCount: 1071`). Results: `probe/results/europe-pmc.json` (12/12 cells,
all pass `probe.schema.validate`).

## 1. Identity and access

- **Base URL:** `https://www.ebi.ac.uk/europepmc/webservices/rest/search`
- **Auth model:** none. Keyless, publicly open EBI service — no API key, no
  OAuth, no header credential of any kind observed or documented.
- **Key requirement:** none. Unlike Crossref/OpenAlex, Europe PMC's `search`
  endpoint takes no `mailto`/polite-pool parameter; `PROBE_CONTACT_EMAIL` is only
  used here to build a courteous `User-Agent` string, not sent as a query param.
- **Published rate limits:** none found. The EBI RESTful Web Service overview
  page (fetched 2026-08-15) documents the endpoint and query syntax but states no
  numeric rate limit, and directs users to a separate PDF Web Service Reference
  Guide and a Developers Forum not fetched here — **treat "no documented limit"
  as unverified-complete, not as "no limit exists."**
- **Observed rate behaviour:** two back-to-back manual `curl` calls without
  inter-request spacing returned `504 Gateway Timeout` (nginx) during this probe;
  every call made with ≥0.5s spacing (the adapter's `RATE`) succeeded, including
  a 12-query coverage pass, a follow-up 12-query detail-capture pass (with one
  transient 504 that a 3s retry cleared), and two ad-hoc verification calls — all
  200s. No `429` was observed; the failures look like transient upstream/load
  timeouts rather than a hard rate-limit rejection. `RATE = 0.5` (matches the
  plan's default) was sufficient; no need to raise it.
- **ToS / attribution:** the RESTful Web Service page requires reading Europe
  PMC's Privacy Notice before use but states no explicit citation format in the
  fetched excerpt. Per-record `license` fields (e.g. `"license":"cc by"` observed
  on several results) suggest attribution follows the underlying work's own
  license, not a blanket API ToS string — **this needs a direct read of Europe
  PMC's terms-of-use page before production use; not independently confirmed
  here.** Compare the plan's framing note: *"the PubMed connector already imposes
  a DOI-link attribution requirement — assume each has its own until verified."*
  Europe PMC's obligation is not yet verified to the same level PubMed's is.

## 2. Mechanics

- **Request/response format:** REST GET, `format=json` (also `xml`/`dc` available,
  not exercised). `resultType=core` returns the full record (abstract, full
  author list, all identifiers, journal/book metadata); `resultType=lite` is a
  smaller projection (not exercised in this probe, but documented — see §6).
- **Pagination:** **cursor-based**, not offset-based. Every response carries
  `nextCursorMark` and a ready-to-use `nextPageUrl`; the first request uses
  `cursorMark=*` (implicit default) and each subsequent page passes the prior
  response's `nextCursorMark`. Confirmed directly in the recorded C1 fixture.
  This is a materially different pagination contract from OpenAlex/Crossref's
  offset+cursor hybrid and needs its own handling in a Layer-2 client.
- **Filtering:** the `query` parameter accepts field-scoped Lucene-like syntax
  (`SRC:MED`, `PUB_TYPE:preprint`, `DOI:"..."`, `EXT_ID:... AND SRC:...`) per
  Europe PMC's documented search syntax. **Verified live in this probe** (see §5)
  — `query=DOI:"10.1080/02646838.2026.2708741"` returned `hitCount: 1`, an exact
  match. Not exercised: date-range filters, `OPEN_ACCESS:y` filtering.
- **Batch support:** none observed. One query per `search` call; no bulk
  multi-query or multi-ID endpoint was found in the surface probed.
- **Error behaviour:** `504 Gateway Timeout` under insufficiently spaced calls
  (transient, cleared on retry); no auth errors possible (keyless); a query with
  zero matches returns a clean `hitCount: 0` with an empty `resultList.result`
  (observed directly for Q3, Q4) rather than an error — well-behaved.
- **A guessed strict-article endpoint failed:** `GET /{source}/{id}/fullTextXML`
  returned `404` for a MEDLINE-only record with no full text. This is expected
  (that endpoint serves full text, not metadata, and only for records with
  full-text availability) — not a working-metadata-lookup path. The metadata
  strict-lookup path is the `query=DOI:"..."` / `EXT_ID:...+AND+SRC:...` pattern
  in §5, not this endpoint.

## 3. Item metadata

Mapped against spec §6.3 (Literature Key Registry) and §6.2 (envelope fields),
from what the **`core` result type actually returned** across the 12-query probe
plus the C1 fixture.

| Registry key / envelope field | Observed | Notes |
|---|---|---|
| `doi` | Present on `MED` and `PPR` records with a registered DOI; absent on some `MED`/`PMC` records (e.g. Q2's top result had no `doi`) — absent when a record predates DOI assignment or the source doesn't register one. | Adapter maps directly from `doi`. |
| `pmid` | Present only on `source: MED` records. | Adapter lifts into `extra_ids["pmid"]`. |
| `pmcid` | Present when the record has a PubMed Central copy (`MED` records with PMC deposit; not on `PPR`). | Adapter lifts into `extra_ids["pmcid"]`. |
| `openalex_id` / `semantic_scholar_id` / `osf_id` / `arxiv_id` | **Never observed.** Europe PMC does not carry cross-connector identifiers for these. | Not in the adapter's `extra_ids`; would need a second-connector join, which the RUBRIC explicitly disallows counting toward `metadata_completeness`. |
| `isbn` | Not observed in this sample (no `NBK`/book-chapter record surfaced). Europe PMC's schema does carry ISBN on book records per its documentation. | Adapter has no ISBN mapping yet — would need `bookOrReportDetails`/book-record handling once an `NBK` record is actually observed. |
| `issn` | **Present in the raw payload but not currently mapped by the adapter.** `journalInfo.journal.issn`/`.essn` was observed on every `MED` journal-article record (e.g. `"issn":"1664-1078"`). | Gap: this is a real, populated field the probe adapter leaves on the floor. Worth mapping in a Layer-2 client. |
| `type` (envelope) | Mapped from `source` (`PPR`→`preprint`, `NBK`→`book`, `MED`→`journal-article`) with a fallback to the raw `pubTypeList.pubType[0]` for anything else — needed because a fourth source code, `PMC`, appeared (see §7) and isn't in the plan's three-way map. | The fallback produced values like `review-article` and, once, the literal string `Abstract` (a malformed-looking `pubType` on a `PMC` record) — see §4 Q2/C2. |
| `venue` | `journalInfo.journal.title` for journal records; `bookOrReportDetails.publisher` for preprints/books (Europe PMC records a preprint's *server* — e.g. "PsyArXiv" — in the same slot a book would carry a publisher). | Reasonably reliable for `MED`; unverified for `NBK` since none was observed. |
| `publisher` | Only populated for `PPR`/book-shaped records via `bookOrReportDetails.publisher`; **never populated for `MED` journal articles** — Europe PMC's `core` result does not expose a journal's publisher name, only its title/ISSN/NLM ID. | A real gap versus Crossref, which does carry `publisher`. |
| `retraction_status` | **Never observed, on any record, of any source type.** No retraction/update-notice field appears anywhere in the `core` payload. | Europe PMC cannot support the envelope's retraction signal (spec §6.2) — Crossref remains the authoritative source for that, exactly as spec §3.5 already designates. |
| `oa_status` | `isOpenAccess: "Y"/"N"` maps to `"open"`/`None`. **Fidelity note:** the adapter only signals `"open"`; a `"N"` (closed) collapses to the same `None` as a genuinely absent field, so a consumer cannot currently distinguish "known closed" from "unknown." Worth a `"closed"` branch in Layer 2. | |

## 4. Measured coverage

All 12 cells, real HTTP calls against `resultType=core`, `pageSize=10` (except
the fixture recording, `pageSize=5`). Full records: `probe/results/europe-pmc.json`.

**`venue_class` and `result` are classified on orthogonal axes** (rubric
clarification ratified 2026-08-15, applied to all five dossiers for
comparability): `result` measures relevance; `venue_class` measures what kind of
artefact the top result *is*, from its own registered metadata, regardless of
whether it answers the query. A miss with a well-formed, DOI-bearing top result
is `venue_class: peer-reviewed-article` (or whatever it actually is) plus a note
explaining the mismatch — **not** collapsed to `unverified` because it missed.
`unverified` is reserved for its literal meaning per spec §6.2's resolution
order: no DOI on the top result (regardless of whether a `pubType` is known), or
a clean zero-result miss with nothing to classify.

| Query | Result | n_results | venue_class | doi_present | Note |
|---|---|---|---|---|---|
| Q1 (IFS) | **miss** | 1,063 | peer-reviewed-article | true | token overlap on "parts"/"protective"; top result is a Chilean gender-identity health-policy paper — well-formed (MED, DOI, named journal), just irrelevant |
| Q2 (SE/Sensorimotor) | **miss** | 180 | unverified | false | token overlap on "window"/"tolerance"; top result is a general distress-theory paper with an empty abstract, `source: PMC`, **no DOI** — unverified for the correct reason (missing DOI), not merely because it missed |
| Q3 (AEDP) | **miss** | 0 | unverified | false | clean zero — nothing to classify |
| Q4 (Heroine's Journey) | **miss** | 0 | unverified | false | clean zero — nothing to classify |
| Q5 (Marston DISC) | **miss** | 1 | peer-reviewed-article | true | single unrelated result (dental-clinic AI-workflow paper) — well-formed (MED, DOI, named journal), just irrelevant |
| Q6 (secure base, established dyads) | **partial** | 161 | peer-reviewed-article | true | top result is "Human-AI attachment" — wrong population (AI, not human romantic dyads) |
| Q7 (Basson desire model) | **partial** | 25 | peer-reviewed-article | true | top result is a sexual-desire-disorder treatment paper; tangential, doesn't center Basson's model |
| Q8 (aesthetic engagement/self-expansion) | **miss** | 222 | peer-reviewed-article | true | token overlap on "aesthetic"/"relational"; top result is wartime group trauma-therapy — well-formed (MED, DOI, named journal), wrong population |
| Q9 (measurement invariance) | **hit** | 5,053 | peer-reviewed-article | true | top result is a genuine psychometric-invariance-testing study |
| Q10 (working memory/fluid intelligence) | **hit** | 8,586 | **preprint** | true | top result is a PsyArXiv preprint (`source: PPR`), directly on-topic |
| C1 (positive control) | **hit** | 1,071 | **preprint** | true | top result is the target EFT-RCT paper — but as a PsyArXiv preprint, not (yet) a journal article |
| C2 (negative control) | **miss** | 79 | unverified | false | adjacent papers only; no construct match — control **passes**. Top result's `pubType` is the malformed-looking literal `"Abstract"`, `source: PMC`, **no DOI** — unverified is correct here for the DOI-absence reason, reinforced (not overridden) by the malformed type |

**Coverage read (excluding C1/C2 per the benchmark's rules):** 2 hits, 2 partials,
6 misses out of 10 coverage queries. The two hits are both quantitative/empirical
(Q9, Q10) — the format/subject axes this benchmark added specifically to close
the Q1–Q8 blind spot. **Every contemporary-clinical, monograph, and historical
query (Q1–Q5) missed.** This matches the pattern already recorded for PubMed in
the 2026-08-14 run and is unsurprising: Europe PMC's index is still fundamentally
biomedical/PubMed-descended, not a general-psychology or humanities index —
adding it does not close the Q1–Q5 gap OpenAlex/Semantic Scholar are positioned
to address.

**Metadata quality is largely intact even on misses.** Three of the five
non-zero misses (Q1, Q5, Q8) returned a fully-formed `MED` record — DOI, PMID,
PMCID, named journal, OA status — that is simply the wrong paper, not a
metadata failure. Only Q2 and C2's top results lacked a DOI (both `source: PMC`,
i.e. not yet MEDLINE-indexed), which is what actually drove their `unverified`
classification, independent of relevance.

**C1 is a structural finding, not just a control pass.** The positive control's
top result is a preprint, not the published journal article Wiebe & Johnson
(2016) would suggest. Europe PMC is fast-indexing 2026 preprints ahead of (or
instead of) the peer-reviewed literature on the same topic — direct evidence
that `venue_class: preprint` must be surfaced to a consumer, not silently
treated as equivalent to a peer-reviewed hit.

## 5. Fuzzy-to-Fact feasibility (ADR-001 §3)

- **`search_works(query)` → ranked candidates:** yes, directly what `/search`
  is. Default sort is relevance; `sort=CITED`/`sort=P_PDATE_D` (date) are
  documented alternatives, not exercised here.
- **`get_work(doi)` strict retrieval — does it accept a DOI as a lookup key?**
  **Yes, verified live in this probe**, via the search endpoint's field-scoped
  query syntax rather than a dedicated single-work endpoint:

  ```
  GET /search?query=DOI:"10.1080/02646838.2026.2708741"&format=json
  → hitCount: 1, exact match (the Q9 top result)
  ```

  An equivalent `EXT_ID:42544915 AND SRC:MED` query (PMID-scoped) also returned
  `hitCount: 1` for the same record — confirming the plan's flagged open
  question ("does it need `EXT_ID`/`SRC`?"): **DOI alone is sufficient** as a
  strict lookup key via `query=DOI:"..."`; `EXT_ID`+`SRC` is an equally valid,
  more source-specific alternative, not a requirement. Neither needs the guessed
  `/{source}/{id}/fullTextXML` endpoint, which serves full text (and 404s when
  none exists), not metadata.
- Because both `search_works` and strict `get_work(doi)` route through the
  *same* `/search` endpoint with different query syntax, a `psychology-mcp`
  wrapper needs only one HTTP client path for both ADR-001 §3 verbs here — a
  simplification relative to Crossref/OpenAlex if they expose them as genuinely
  separate endpoints.

## 6. FastMCP wrapping feasibility (ADR-001 §2, §7)

- **Async-native REST:** yes. Plain `GET` + JSON over HTTPS, no SDK, no
  session/cookie state required beyond what any HTTP client provides — trivially
  wrappable with `httpx.AsyncClient`, no `run_in_executor` needed.
- **Batch support:** none (§2) — an agent needing N works makes N calls; no
  batch discount or bulk endpoint to design around.
- **Rate limits under agent concurrency:** no published hard limit (§1), but the
  observed 504s under unspaced calls mean a `psychology-mcp` wrapper **must**
  still serialize or rate-limit its own outbound calls per §1's `RateLimiter`
  pattern — "no documented limit" is not "safe to fire concurrently."
- **Slim mode expressible?** **Yes, directly** — `resultType=lite` vs `core` is
  exactly the mechanism spec §6.4's slim triple (`doi`, `title`, `venue_class`)
  needs: request `lite` for a slim/triage pass, `core` only when full metadata
  is needed. Not exercised live in this probe (only `core` was fetched), but the
  parameter is documented and its purpose is exactly this distinction — flag as
  a design-time assumption to confirm with one live `resultType=lite` call
  before Layer 2 relies on it.
- **Cursor pagination (§2)** is a genuine wrapping cost: a FastMCP tool would
  need to either expose `cursorMark` to the caller or manage cursor state
  server-side across paginated calls — more design work than an offset-based API.

## 7. Existing MCP server, and the supersede-vs-complement question (spec §10 q1)

**Does a public MCP server exist for Europe PMC?** A third-party listing was
found: **"Europe PMC MCP Server & Skill"** at `mcpbundles.com`
(`https://mcp.mcpbundles.com/bundle/europe-pmc`), advertising 4 tools, keyless,
built on Europe PMC's open API. This is a **community-run bundle wrapper, not an
EBI/Europe-PMC-maintained server**, and its liveness/reliability was **not
independently tested in this probe** (found via search, not connected to). No
EBI-maintained or otherwise first-party Europe PMC MCP server was found.

Contrast: `bio-research/.mcp.json` already declares a **first-party,
Anthropic-hosted** `pubmed` server (`https://pubmed.mcp.claude.com/mcp`) — live,
credentialed by nothing (keyless), and already in production use (the
2026-08-14 run that produced this benchmark's Q1–Q6 bound it directly, and this
session has direct tool access to it, `mcp__claude_ai_PubMed__*`). Any Europe
PMC binding competes against a materially more mature existing option, not a gap.

### Supersede vs. complement — the evidence

`source` values observed across the top-10-per-query sample of all 12 queries
(91 items total; Q3/Q4 contributed 0 since both were clean zero-hit misses):

| `source` | Count | Share | Meaning |
|---|---|---|---|
| `MED` | 75 | 82.4% | MEDLINE/PubMed-indexed — **this is what a PubMed binding already covers** |
| `PMC` | 10 | 11.0% | In PubMed Central but **not (yet) MEDLINE-indexed** — invisible to a PubMed-only binding |
| `PPR` | 6 | 6.6% | Preprint — invisible to a PubMed-only binding |
| `NBK` | 0 | 0% | NCBI Bookshelf — **not observed at all** in this 12-query psychology benchmark |

**17.6% of the sampled results (`PMC` + `PPR`) would not exist in a PubMed-only
binding.** That is not marginal, and it is not evenly distributed: `PPR` records
were the **top (rank-1) result** for two of the twelve queries — Q10 (a genuine
coverage hit) and **C1, the positive control itself**. A PubMed-only binding
would have returned the *second-ranked* result for C1, not the top one; Q10's
top hit would likely have been altogether absent from a PubMed-only result set
depending on whether a later MEDLINE-indexed paper covers the same ground.

`NBK` (Bookshelf) — the other half of the plan's stated evidence target,
alongside `PPR` — was **never observed** in this benchmark. That is itself a
finding, not a gap in the probe: Bookshelf skews toward clinical
monographs/guidelines (e.g. StatPearls, treatment manuals), and none of the 12
queries' top-10 pages surfaced one. This benchmark cannot confirm Europe PMC's
Bookshelf coverage adds value for *this* psychology query mix, even though the
API's documented scope includes it.

**Verdict: Europe PMC complements a PubMed binding; it does not supersede one
outright, but it is the stronger single choice if only one biomedical-leaning
connector is bound.** Reasoning:

1. Europe PMC's `MED`-sourced records are (per EBI's own indexing pipeline)
   MEDLINE-derived — the 82.4% `MED` share here is not independent coverage,
   it is the same underlying PubMed data reachable through a different API.
   Binding Europe PMC **instead of** PubMed loses nothing on that 82.4%.
2. The 17.6% `PMC`+`PPR` share, plus two top-ranked misses a PubMed-only binding
   would suffer (Q10, C1), is real incremental coverage a PubMed-only binding
   cannot reach — this is the concrete evidence for "replace," not merely
   "add."
3. But the *existing* `pubmed` binding (§7 above) is first-party, live, and
   already integrated (`bio-research`, this session's tool access); Europe PMC's
   only comparable server option is an unverified third-party community bundle.
   Recommending an outright swap trades a proven binding for an unproven one on
   the server-availability axis, even though the underlying API is well-behaved.
4. `retraction_status` is never exposed by Europe PMC (§3) — a property a
   PubMed-derived binding could plausibly carry (PubMed surfaces retraction
   notices) and Europe PMC's `core` payload does not. Not independently
   confirmed for the existing `pubmed` MCP server's actual tool surface, but
   worth checking before treating this as a pure upgrade.

Net: the coverage case for Europe PMC over a bare PubMed binding is real and
quantified (17.6% incremental, including 2/12 top-ranked-result misses), but
"supersede" is a Layer-2 build decision, not a foregone conclusion from this
data alone — it should be wrapped as `psychology-mcp`'s own gateway (§8) rather
than treated as a drop-in replacement for the existing third-party `pubmed`
server declaration.

## 8. Recommendation

**Wrap.** Europe PMC should be wrapped as a first-party `psychology-mcp` tool
(`search_works`/`get_work(doi)` per §5), not bound via a third-party server and
not dropped.

**Reasoning:**
- Keyless, well-behaved REST, async-native, cursor pagination is the only real
  wrapping cost (§6) — low implementation effort.
- Delivers real incremental scope beyond a PubMed-only binding: 17.6% of sampled
  results outside `MED`, including the top-ranked result on 2/12 queries (§7).
- The only existing MCP server for it is an unverified third-party community
  bundle (§7) — not a credible bind target for production use without its own
  verification pass, which is out of scope here.
- It does **not** close this benchmark's biggest gap: Q1–Q5
  (contemporary-clinical, monograph, historical) still miss, because Europe
  PMC's index remains biomedical/PubMed-descended (§4). It is not a substitute
  for OpenAlex/Semantic Scholar coverage of that literature.
- It cannot carry `retraction_status` or `publisher` for journal articles (§3),
  so Crossref remains the authoritative source for the venue-classification
  envelope exactly as spec §3.5 already designates — Europe PMC does not change
  that division of labor.

**Residual risk:**
- The ToS/attribution obligation is not fully verified (§1) — confirm before
  shipping any consumer-facing citation text sourced from Europe PMC records.
- `resultType=lite` (the slim-mode mechanism, §6) was never exercised live —
  confirm its field set matches spec §6.4's slim triple before relying on it.
- The `PMC`-source `type` fallback produced a malformed-looking value
  (`"Abstract"`, on C2's top result, §3/§4) — a Layer-2 parser needs a cleaner
  fallback than raw `pubType[0]` for non-`MED`/`PPR`/`NBK` sources.
- Zero `NBK` records were observed (§7) — the "plus NCBI Bookshelf monographs"
  part of Europe PMC's candidate rationale (spec §3.5) is **unconfirmed by this
  benchmark**, not established. If Bookshelf coverage specifically matters to a
  future query set, re-run with monograph/guideline-shaped queries before
  relying on it.
