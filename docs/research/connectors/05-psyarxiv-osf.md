# PsyArXiv / OSF — connector dossier

Probe artifacts: `probe/connectors/osf.py` · `probe/tests/test_osf.py` ·
`probe/fixtures/psyarxiv-osf-C1.json` · `probe/results/psyarxiv-osf.json`

All 12 cells were fetched from the live `api.osf.io` API on 2026-08-15
(`retrieved_at` range `2026-08-15T21:11:37Z`–`2026-08-15T21:11:48Z`, `RATE = 1.0`s,
never throttled). No result was extrapolated or invented; every cell in
`probe/results/psyarxiv-osf.json` traces to an actual HTTP response recorded by
`python3 -m probe.run --connector psyarxiv-osf`, and all 12 came back `miss`,
`n_results: 0` — a real, reproducible finding about the route's search mechanics
(§2, §5), not a probe defect.

**Total real HTTP calls made in this task: 41** — 36 against `api.osf.io`, 5
against `api.crossref.org` for the §3 cross-check. Breakdown of the 36 OSF calls:
1 initial fixture capture (later superseded), 12 for the recorded benchmark run,
and 23 supplementary investigation calls made to characterise the actual search
surface before trusting `filter[title]` — see §2 and §5 for what each one showed:
`filter[q]` (rejected, 400), a bare `filter[provider]` listing (baseline), the
top-level `q=` trap (§2), `/v2/search/` (404), `/v2/` root capability listing,
single-word vs. multi-word `filter[title]` probes (`therapy`, `Window`, `couples`,
`"couples therapy"`, `evidence-based`, `outcome`, `"window of tolerance"`,
`attachment`, `depression`, `anxiety`, `personality`, `review`), a `page[size]=10`
listing used to surface real DOI-bearing preprints, one full preprint detail
fetch (`/v2/preprints/xe2mz_v5/`), and one response-header capture for rate-limit
evidence. First real response (initial C1 probe, before the search-surface was
understood, truncated to 220 chars): `{"data":[],"links":{"first":null,"last":null,"prev":null,"next":null,"meta":{"total":0,"per_page":5}},"meta":{"version":"2.0"}}`.
Last real response (Crossref cross-check for `10.1038/s44271-026-00515-7`,
truncated to 220 chars): `{"status":"ok","message-type":"work","message-version":"1.0.0","message":{"indexed":{"date-parts":[[2026,7,27]],"date-time":"2026-07-27T15:03:25Z","timestamp":1785164605761,"version":"3.55.0"},"reference-count":0,"publis`.

## 1. Identity and access

- **Base URL:** `https://api.osf.io/v2/preprints/` (this dossier covers the
  `preprints` collection filtered to `filter[provider]=psyarxiv`, per the
  benchmark's psychology-preprint scope — spec §3.5).
- **Auth model:** Keyless for read access. Confirmed live — all 36 calls in this
  task succeeded with no Personal Access Token, using only a descriptive
  `User-Agent` (this probe adds no OSF-specific auth header; `base.py`'s shared
  `build_headers` was sufficient).
- **Rate limits:** no `X-RateLimit-*` or `Retry-After` headers were present on
  any observed response (confirmed via a dedicated header capture, §1 call
  count above) — OSF does not expose rate-limit telemetry inline the way some
  APIs do. Per web-search corroboration from two independent sources (a COS
  community GitHub issue and a third-party API guide, not confirmed against
  OSF's own primary docs, which render client-side and were not machine-
  readable via fetch): **unauthenticated requests are capped at ~100/hour**;
  **authenticated (Personal Access Token) requests at ~10,000/day**. This
  probe's `RATE = 1.0` (1 req/s) never came close to the unauthenticated hourly
  ceiling across a 12-call benchmark run and no 429 was observed across all 36
  calls in this task (several bursts faster than 1/s during exploratory
  `curl` calls, which sit outside the adapter's own `RateLimiter`) — `RATE` was
  not raised. **A production `psychology-mcp` wrapper should authenticate with
  a PAT** if it expects sustained call volume; the 100/hour anonymous ceiling
  would be tight for a multi-agent workload.
- **ToS / attribution:** `https://osf.io/terms-of-use/` requires agreeing to the
  Terms of Use to use the Public API at all, but no OSF-API-specific
  display-attribution clause (of the kind the plan flags for the PubMed
  connector's DOI-link requirement) was found in what could be fetched. Content
  licensing is **per-item**, not API-wide: every preprint record carries its own
  `license_record` (observed live on `xe2mz_v5`: `{"copyright_holders": [],
  "year": null}` — present but often unpopulated), so a consumer displaying
  full text or reusing content (not just metadata) needs to check the specific
  preprint's license, not assume a blanket CC0/CC-BY grant the way OpenAlex's
  metadata is CC0 (`02-openalex.md` §1).

## 2. Mechanics

- **Request/response format:** plain HTTP GET, **JSON:API** response
  (`Content-Type: application/vnd.api+json`) — the only one of the five
  connectors in this program using JSON:API rather than a bespoke JSON shape.
  Every record lives at `data[].{id, type, attributes, relationships, links}`,
  not a flat object — the extra `attributes` nesting is why the adapter's
  `parse()` unwraps `rec.get("attributes")` before reading any field (unlike
  the other four adapters, which read top-level record keys directly).
- **The real search surface — this is the central finding of this dossier.**
  Three routes were investigated live before settling on the adapter's actual
  request shape:
  1. **`filter[title]=<query>`** — real, and it *is* what the adapter uses, but
     it is a **literal, case-insensitive SUBSTRING match against the `title`
     field only**, not a tokenized/boolean word search and not full-text.
     Confirmed by a minimal-pair test: `filter[title]=couples` → **73** matches
     (substring found inside e.g. "Romantic Couples"); `filter[title]=couples
     therapy` (two words, one space) → **0** matches, even though PsyArXiv
     unquestionably has preprints about couples therapy (verified separately
     via `filter[title]=therapy` → 693 matches, several about couple/relational
     therapy). The two-word phrase has to occur **contiguously and verbatim**
     in a title; real titles essentially never contain a 5–10 word natural-
     language query string verbatim, which is why every one of this
     benchmark's Q1–Q10/C1/C2 queries — all multi-word phrases — returned
     `n_results: 0`.
  2. **A top-level `q=` parameter is a silent no-op trap, not a search route.**
     `?filter[provider]=psyarxiv&q=emotionally focused therapy...` returns
     HTTP 200 with `total: 62651` and a result list; so does
     `?filter[provider]=psyarxiv&q=zzzznonsensequeryxyz123`; so does the same
     request with **no `q=` at all**. All three returned the byte-identical
     first three titles and the identical total. `q` is simply an
     unrecognised query parameter that OSF's JSON:API layer ignores rather
     than rejects, and the endpoint falls back to its default (apparently
     newest-first) ordering. A naive adapter author who tried `q=` first and
     saw HTTP 200 with a non-empty `data[]` could easily mistake this for a
     working full-text search and silently ship a connector that always
     returns "whatever's newest," mislabelled as query results. **This adapter
     does not use `q=`, for exactly that reason.**
  3. **`filter[q]=<query>`** — rejected outright: HTTP 400,
     `"'q' is not a valid field for this endpoint."` Not a silent trap like
     (2), at least — it fails loudly.
  4. **No dedicated search endpoint exists.** `GET https://api.osf.io/v2/search/`
     → HTTP 404. The `/v2/` root's capability listing (`nodes`, `users`,
     `collections`, `registrations`, `institutions`, `licenses`, `schemas`,
     `addons`) advertises no `search` link. OSF's own web frontend
     (`preprints.osf.io`'s "Discover" page) is understood to be backed by a
     separate Elasticsearch-based discovery service (historically
     `share.osf.io`), not by anything exposed on the public `api.osf.io/v2/`
     surface probed here; that service was out of scope for this dossier
     (different host, different auth/rate posture, not documented as part of
     the `preprints` resource this benchmark targets) and is flagged as an
     open question for the Layer-2 build rather than something this probe
     silently assumed away.
  **Conclusion: `filter[title]=query`, used exactly as the plan specified, is
  the best available mechanism on this route, and it is a retrieval-by-
  substring filter, not a ranked-relevance search.** See §5 for what this
  means for Fuzzy-to-Fact feasibility.
- **Pagination:** JSON:API-standard — `page[size]`, `page[number]` (not
  exercised beyond `page[size]`), plus `links.meta.total` for the grand total
  and `links.{first,prev,next,last}` for cursor-style traversal. The adapter
  reads `links.meta.total` for `Response.total` (confirmed correct against a
  non-empty result set, e.g. `filter[title]=therapy` → `links.meta.total: 693`
  matched the observed page contents).
- **Filtering:** JSON:API bracketed filter syntax, `filter[<field>]=<value>`,
  confirmed to correctly URL-encode and be honoured server-side for
  `filter[provider]` and `filter[title]` (both exercised live). Filters appear
  to AND together (not tested exhaustively — only two filters were combined in
  this pass).
- **Slim/field selection:** not exercised in this pass; JSON:API's standard
  `fields[type]=a,b,c` sparse-fieldset mechanism is documented for the OSF API
  generally (per the guide summarised in §7) but was not confirmed live against
  the `preprints` collection here — an open item for the Layer-2 build, not an
  assumed-working claim.
- **Batch:** no multi-ID batch-fetch route was exercised; JSON:API commonly
  supports `filter[id]=id1,id2` for this pattern but it was not tested live.
- **Error behaviour:** `filter[q]` produced a clean, structured JSON:API error
  object (`errors[].detail`, `.source.parameter`, `.status`) on HTTP 400 — this
  is the one negative case actually observed; a raw unrecognised-record 404 was
  not exercised (no bad preprint ID was requested).

## 3. Item metadata

**Formal benchmark result:** because all 12 cells returned `n_results: 0`,
`metadata_completeness` is empty `[]` for every one of the 12 recorded rows —
there is nothing in an empty `data[]` to report metadata coverage from. This is
itself the headline metadata finding for the benchmark specifically: a
substring-only route cannot be scored on richness of records it never returns.

**Supplementary schema observation (outside the 12 formal cells, made to
characterise what the route returns *when it does* match — not counted as a
13th coverage cell):** fetching real PsyArXiv preprints via single-word
`filter[title]` matches (`therapy`, `attachment`, `personality`, etc.) and one
full detail fetch (`GET /v2/preprints/xe2mz_v5/`) surfaced:

| Registry/envelope field | Observed | Source path |
|---|---|---|
| `doi` | present on a minority of records; **null on most recent (2026) preprints** | `attributes.doi` — see finding below, this is not a reliable preprint-specific identifier |
| `osf_id` | present on every record | `data[].id` (e.g. `xe2mz_v5`) |
| `type` (envelope) | not returned by the API as a classifiable field on this route — every record is a PsyArXiv preprint by construction, which is why the adapter hardcodes `type="preprint"` per the plan | n/a |
| `venue` (envelope) | not returned per-record; the adapter hardcodes `"PsyArXiv"` since `filter[provider]=psyarxiv` is fixed | n/a |
| `publisher` (envelope) | not returned per-record; the adapter hardcodes `"Center for Open Science"` | n/a |
| `retraction_status` | `date_withdrawn` exists as a field (null on all records observed) — a real withdrawal signal, not captured by the current adapter's `Item.retraction_status` | `attributes.date_withdrawn` |
| `oa_status` | not returned as a discrete field; the adapter hardcodes `"open"` (structurally true — PsyArXiv preprints are open access by provider policy) | n/a |
| `pmid`, `pmcid`, `openalex_id`, `semantic_scholar_id`, `arxiv_id`, `isbn`, `issn` | not observed on any record | OSF preprints do not surface any registry key besides its own `osf_id` and (sometimes) `doi` |

**Finding — `attributes.doi` is not a trustworthy preprint-specific
identifier, and this directly affects the adapter's `type="preprint"`
assumption.** Fetching `GET /v2/preprints/xe2mz_v5/` in full showed
`"doi": "10.1016/j.paid.2026.114032"` (an Elsevier journal DOI) alongside
`"preprint_doi_created": null` — OSF never minted its own `10.31234/osf.io/...`
DOI for this item; instead, once the preprint was linked to its published
version, the `doi` field was populated with the **published article's** DOI,
not a preprint-specific one. The §3 Crossref cross-check below confirms this
independently: Crossref classifies that same DOI as `type: "journal-article"`
in the *`Personality and Individual Differences`* journal, and its `relation`
object explicitly lists `has-preprint` pointing at two **different** DOIs
(`10.31234/osf.io/xe2mz_v4` and `.../xe2mz_v5`) — the actual OSF-minted
preprint identifiers, never returned by the `preprints` list route we queried.
**Consequence:** this adapter's `type="preprint"` (mandated by the plan,
"everything from this route is a preprint by construction") is correct about
*provenance* (the item was retrieved via the PsyArXiv preprints collection) but
can be wrong about *current bibliographic status* (per RUBRIC.md's own
principle — "decide from the item's own registered metadata, never from the
... index that surfaced it" — the registered metadata for this DOI says
`journal-article`). A Layer-2 server resolving `venue_class` from the OSF
`doi` field verbatim would silently misclassify a published article as a
preprint whenever OSF has back-filled the published DOI into that field.

**Crossref cross-check (spec §3.5) — how much preprint metadata survives
across indexers.** Five real PsyArXiv-preprint DOIs (surfaced via the
supplementary `filter[title]` searches above, not the 12 formal misses, since
none of the 12 formal cells returned a DOI to check) were queried against
`https://api.crossref.org/works/{doi}` live, 1 req/sec, `mailto=$PROBE_CONTACT_EMAIL`:

| PsyArXiv DOI (from `attributes.doi`) | Crossref `type` | Crossref `container-title` | Crossref `publisher` | `relation.has-preprint`? |
|---|---|---|---|---|
| `10.1016/j.paid.2026.114032` | `journal-article` | *Personality and Individual Differences* | Elsevier BV | **yes** — points to `10.31234/osf.io/xe2mz_v4` and `_v5` |
| `10.1177/08902070261476539` | `journal-article` | *European Journal of Personality* | SAGE Publications | **yes** — points to `10.31234/osf.io/tjqv8_v2` and `_v3`, plus 6 open-review `has-review` DOIs |
| `10.1038/s44271-026-00515-7` | `journal-article` | *Communications Psychology* | Springer Nature | no `relation` present |
| `10.36948/ijfmr.2026.v08i01.65598` | `journal-article` | *International Journal For Multidisciplinary Research* | IJFMR | no `relation` present |
| `10.71097/IJAIDR.v17.i2.2048` | `journal-article` | *Journal of Advances in Developmental Research* | International Research Publication and Journals | no `relation` present |

**All five resolved cleanly at Crossref** (HTTP 200, well-formed metadata) —
every DOI OSF surfaced is a real, registered Crossref DOI, so basic identity
metadata (title, container, publisher, ISSN, issue date) fully survives across
indexers. But **zero of the five are classified `posted-content`/preprint at
Crossref** — all five are `journal-article`, because (per the finding above)
`attributes.doi` on a *published* PsyArXiv preprint holds the published-version
DOI, not the preprint's own. Two of the five carry an explicit
`relation.has-preprint` back-reference to the *actual* OSF preprint DOI,
proving the two are genuinely distinct, separately-Crossref-registered records
— confirming this is a real identifier-conflation, not a one-off data-entry
error. **What survives:** title, venue, publisher, ISSN, publication date —
fully, on all five. **What does not survive, or actively contradicts OSF's own
`type="preprint"` framing:** venue classification itself. A consumer relying on
OSF alone would tag all five `preprint`; Crossref (the RUBRIC's own
authoritative source for `venue_class`) says `journal-article` for all five.

## 4. Measured coverage

| Query | Result | n_results | venue_class | Notes |
|---|---|---|---|---|
| Q1 IFS therapy | **miss** | 0 | unverified | substring-only filter; multi-word phrase not found verbatim in any title |
| Q2 Somatic Experiencing / window of tolerance | **miss** | 0 | unverified | same mechanism |
| Q3 AEDP / Fosha / transformance | **miss** | 0 | unverified | same mechanism |
| Q4 Heroine's Journey / Murdock / Frankel | **miss** | 0 | unverified | same mechanism |
| Q5 Marston 1928 / DISC | **miss** | 0 | unverified | same mechanism |
| Q6 secure base / safe haven, established dyads | **miss** | 0 | unverified | same mechanism |
| Q7 Basson responsive desire | **miss** | 0 | unverified | same mechanism |
| Q8 aesthetic engagement / self-expansion | **miss** | 0 | unverified | same mechanism |
| Q9 measurement invariance / scale validation | **miss** | 0 | unverified | same mechanism |
| Q10 working memory / fluid intelligence | **miss** | 0 | unverified | same mechanism |
| C1 EFT couples (positive control) | **miss** | 0 | unverified | **not a broken client** — re-verified directly against the live API outside the harness, identical HTTP 200 + empty `data[]`; PsyArXiv does host EFT/couples-therapy preprints (confirmed via `filter[title]=therapy`), but none carry the C1 query string verbatim as a title substring. Per this task's brief, scored as a search-surface finding for this connector, not a coverage gap, and not diagnosed as an adapter bug |
| C2 fabricated construct (negative control) | **miss (pass)** | 0 | unverified | zero results — clean pass per the README's three-outcome C2 rule; no adjacent-match false positive to report, but also no discriminative signal (every query misses this route the same way) |

**Coverage tally (Q1–Q10 only, C1/C2 excluded per README's "C1 is scored
separately"): 0 hit / 0 partial / 10 miss.** This is a uniform-zero result
across the entire coverage set, including the positive control — the flattest,
least-informative row in the eventual coverage matrix, and that flatness *is*
the finding: this route cannot be scored on topical recall at all, because it
never reaches the point of returning candidates to evaluate topically.

## 5. Fuzzy-to-Fact feasibility (ADR-001 §3)

**Candid answer: this route cannot support Fuzzy-to-Fact Phase 1
(`search_works(query)` → ranked relevance candidates) as specified, at all.**
Phase 1 presumes a ranked, relevance-scored candidate list for an ambiguous
natural-language query. `filter[title]` is not that — it is a **retrieval-by-
substring** interface: it returns the literal set of records whose title
contains the filter value, unordered by relevance (default ordering appears to
be recency, per the `q=` no-op test in §2), and it returns **nothing** the
instant the query is phrased as a multi-word natural-language string rather
than a literal substring, which is exactly the shape every Fuzzy-to-Fact Phase
1 query would arrive in. §4's 10/10 coverage misses are not a tuning problem —
lowering the `limit`, retrying, or reformulating slightly would not fix a
fundamentally substring-based filter.

- **`search_works(query)` → ranked candidates:** **no**, not on this route.
  What would be needed instead is a different index in front of it — either
  (a) an OSF-hosted full-text/discovery service (the `share.osf.io`-style
  Elasticsearch backend referenced in §2, unconfirmed as still live or
  publicly reachable — a real open question, not assumed away), or (b) a
  Layer-2-side tokenized query strategy: decompose the natural-language query
  into individual significant keywords and issue several `filter[title]=<word>`
  calls, unioning and re-ranking client-side (confirmed live in this dossier's
  investigation: single words like `therapy`, `couples`, `attachment` each
  return dozens to hundreds of matches). That is a workaround this project
  could build, not a capability OSF's `preprints` route itself provides.
- **`get_work(doi)` strict lookup:** **yes, structurally** — OSF's detail route
  `GET /v2/preprints/{id}/` (confirmed live, §3) is a clean strict-retrieval
  shape, but it is keyed on the **OSF id**, not the DOI, and was not confirmed
  to accept a bare DOI as a lookup key in this pass. Combined with §3's finding
  that `attributes.doi` on a published item is often the *published* DOI, not
  the OSF-minted preprint DOI, a Layer-2 `get_work(doi)` implementation would
  need to resolve which DOI it was given (OSF-minted `10.31234/osf.io/...` vs.
  a downstream publisher DOI) before it could reliably route to the right OSF
  record — not a simple pass-through.

## 6. FastMCP wrapping feasibility (ADR-001 §2, §7)

- **Async-native REST:** yes — plain HTTP GET/JSON:API, no vendor SDK, no
  session state; wraps cleanly with `httpx.AsyncClient` per ADR-001 §2, same as
  the other four connectors.
- **Batch endpoint:** not confirmed live in this pass (§2); JSON:API's
  `filter[id]=a,b,c` convention is a plausible route, unverified here.
- **Rate limits under agent concurrency:** the ~100/hour unauthenticated
  ceiling (§1, secondary-sourced) would be genuinely tight for a multi-agent
  workload hitting this connector repeatedly — this is the one connector in
  this program where authenticating with a Personal Access Token is likely
  **required**, not merely a courtesy (contrast OpenAlex's generous 100 req/s
  keyless ceiling, `02-openalex.md` §1).
- **Slim mode expressible:** unconfirmed live (§2) — JSON:API sparse
  fieldsets (`fields[preprints]=title,doi`) are the documented mechanism but
  were not exercised against this collection in this pass.
- **The deeper wrapping problem is not mechanical, it is architectural:** even
  a perfectly-wrapped `filter[title]` tool would hand a Layer-2 consumer a
  substring-match primitive where every other connector in this program hands
  back a relevance-ranked list. A `psychology-mcp` server exposing this as
  `search_works` without a loud caveat in the tool description would silently
  mismatch caller expectations — the tool needs to be named and documented as
  what it is (a title-substring filter over PsyArXiv), not presented as
  equivalent to the other four connectors' search tools.

## 7. Existing MCP server

One relevant public MCP server was found (web search, 2026-08-15):

| Repository | Notes |
|---|---|
| `matsjfunke/paperclip` | MCP server explicitly covering arXiv, the OSF API, and OpenAlex, with PsyArXiv named among 30+ supported OSF-partnered preprint providers (PaleoRxiv, SocArXiv, SportRxiv, Thesis Commons, etc.). Keyless — repo states no authentication is needed. 29 stars, 10 forks. **Archived by the owner on 2025-12-16 and now read-only**; its previously-hosted public instance is stated as no longer available — a user would have to self-host it (Docker/Docker-Compose and a GitHub Actions VPS-deploy workflow are provided). |

Not affiliated with the Center for Open Science, not verified live in this
pass (name/stars/license/archived-status only, via web fetch — the server
itself was not called). This is prior art worth knowing about (someone already
solved the "which OSF filters map to which preprint providers" plumbing) but
**not currently bindable** — there is no live, maintained public instance to
bind to, only an archived, self-host-only repository. No first-party MCP
server from the Center for Open Science was found.

## 8. Recommendation: **drop for Fuzzy-to-Fact search; conditionally wrap for
strict retrieval only**

Not a clean wrap/bind/drop — the honest answer differs by capability:

**Drop, for the ranked-relevance search role this program's other four
connectors fill.** §5 is unambiguous: `filter[title]` is a substring filter,
not a search index, and §4 shows what that costs empirically — a 0/10
coverage tally including the positive control, the only such result among the
five connectors probed in this program. Building a `search_works` tool on top
of it would either (a) return empty for almost every realistic natural-
language query, exactly as observed, or (b) require building a client-side
keyword-decomposition-and-rerank layer that is really a second connector's
worth of engineering bolted onto a thin REST call — out of scope for a
Layer-1 wrap decision (spec §3.2 non-goal: do not build `psychology-mcp`
itself here, and this finding says the *design* for that layer would need to
be non-trivial, which is exactly the kind of thing this discovery phase exists
to surface before Layer 2 commits to an approach).

**Conditionally wrap, narrowly, for identifier-anchored lookup and
cross-reference completeness** — *if* a Layer-2 consumer already has an OSF id
or a confirmed OSF-minted DOI (e.g. surfaced via Crossref's `relation.has-
preprint`, §3) and needs to retrieve that specific preprint's record (open-
access status, version history, license, data/prereg links — real fields
observed live in §3 that no other connector in this program returns). That is
a strict-retrieval, not fuzzy-search, use case, and OSF is the *only*
authoritative source for it.

**Reasoning:**
- The search-surface finding (§2, §5) is structural, not a tuning problem or
  an adapter bug — confirmed by directly re-testing the exact C1 query outside
  the harness and by the minimal-pair substring test (`couples` hits, `couples
  therapy` misses).
- The `attributes.doi`/`type="preprint"` conflation (§3) means even the
  narrow retrieval use case needs a downstream Crossref check before trusting
  `venue_class`, which somewhat undercuts "OSF is authoritative for OSF
  records" — it is authoritative for *provenance and non-bibliographic
  metadata* (open-access status, data/prereg links, version history), not
  reliably for *current publication status*.
- No live bindable MCP server exists (§7) — `paperclip` is archived with no
  hosted instance, so binding isn't actually available even where it would
  otherwise be attractive.

**Residual risks:**
1. **If a future Layer-2 build discovers a working OSF/PsyArXiv full-text
   discovery route** (the `share.osf.io`-style backend referenced but not
   confirmed reachable in §2), this recommendation should be revisited — the
   "drop for search" conclusion is scoped specifically to the
   `api.osf.io/v2/preprints/` route probed here, not to PsyArXiv's corpus
   being unreachable in principle.
2. **The ~100/hour unauthenticated rate limit is secondary-sourced** (§1) —
   not confirmed against OSF's own primary docs (which render client-side and
   resisted automated fetch in this pass). Worth a direct re-check, and worth
   provisioning a Personal Access Token, before any production build depends
   on this number.
3. **Only 5 DOIs were cross-checked against Crossref** (§3), all surfaced via
   supplementary single-word searches outside the formal 12-cell benchmark
   (the 12 formal cells returned zero DOIs to check, by construction of the
   §4 miss rate) — real, live-verified evidence, but a small, opportunistic
   sample, not a systematic audit of how often OSF's `doi` field is
   preprint-own vs. published-version.
4. **Sparse fieldsets/slim mode and batch fetch were never exercised live**
   (§6) — assumed plausible from JSON:API convention, not confirmed for this
   specific collection.
