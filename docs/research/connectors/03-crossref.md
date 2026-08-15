# 03 — Crossref

Method, benchmark, and cell schema: [`README.md`](README.md). Classification rubric applied
below: [`probe/RUBRIC.md`](probe/RUBRIC.md). Adapter: [`probe/connectors/crossref.py`](probe/connectors/crossref.py).
Validated cells: [`probe/results/crossref.json`](probe/results/crossref.json). Recorded fixture:
[`probe/fixtures/crossref-C1.json`](probe/fixtures/crossref-C1.json).

**Crossref is not merely another coverage index in this roster.** Spec §6.2 makes Crossref
the resolution authority for `venue_class` and retraction status across the whole literature
envelope — every other connector's items get classified through registered Crossref-style
metadata, and §3 below is the direct evidence base for that design decision.

## 1. Identity and access

- **Base URL**: `https://api.crossref.org/works` (collection search) and
  `https://api.crossref.org/works/{doi}` (single-work strict lookup — verified live, §5).
- **Auth model**: none. Fully keyless. The "polite pool" is opt-in via a `mailto` query
  parameter or a `mailto:` token in the `User-Agent` header — both were set on every call
  in this probe (`PROBE_CONTACT_EMAIL=dwbranson@gmail.com`).
- **Key requirement**: none, ever. This is a genuine no-credential connector, unlike
  Semantic Scholar's unauthenticated-but-throttled posture.
- **Published + observed rate limits**: response headers on every call in this session
  (verified live, not from docs) carried `x-rate-limit-limit: 3`, `x-rate-limit-interval: 1s`,
  `x-concurrency-limit: 3`, `x-api-pool: polite-array` — confirming the `mailto` parameter
  routed the request into the polite pool. The adapter's initial `RATE = 0.2` (5 req/s) did
  **not** trigger a 429 across the 12-cell run, but it exceeds the server's declared 3 req/s
  cap, so it was tightened post-hoc to `RATE = 0.35` (~2.9 req/s) to stay under the observed
  limit with margin — see the comment in `crossref.py`. No throttling was observed at either
  setting in this session; the change is precautionary, grounded in the header evidence.
  Anonymous (non-polite) requests are documented by Crossref to receive a materially lower,
  unspecified limit — not tested here since `mailto` was set throughout.
- **ToS / attribution**: Crossref's terms ask for a `mailto` contact and a descriptive
  `User-Agent` for polite-pool access (both honored by `probe/connectors/base.py`'s shared
  `USER_AGENT` + this adapter's `mailto` param) but impose **no per-record attribution
  requirement** comparable to PubMed's DOI-link rule — Crossref metadata is explicitly
  intended for redistribution and reuse as a bibliographic registry.

## 2. Mechanics

- **Request format**: plain query-string GET. `query=<terms>&rows=<n>&mailto=<contact>` for
  search; `/works/{doi}` (URL-escaped DOI) for strict lookup. No POST/batch body format.
- **Response format**: JSON, `{"status", "message-type", "message": {...}}`. For search,
  `message` = `{"total-results": int, "items": [...]}`; for single-work lookup, `message` is
  the work object directly (not wrapped in a list) — confirmed live in §5.
- **Pagination**: offset/limit via `rows` + `offset`, or cursor-based deep paging via
  `cursor=*` for large result sets (not exercised here; all 12 queries used `rows=10` or
  `rows=5`, well under any pagination boundary).
- **Filtering**: a rich `filter=` query language — `type:journal-article`,
  `from-pub-date:`, `has-full-text:true`, and, load-bearing for §3 below,
  **`filter=update-type:retraction`**, which was used live to locate a real retracted work.
- **Batch support**: no true multi-DOI batch endpoint in the public `/works` route (contrast
  OpenAlex's `filter=ids.openalex:ID1|ID2`); N single-work lookups is the fallback for
  DOI-list resolution.
- **Error behaviour**: unresolvable DOI on `/works/{doi}` returns HTTP 404 with a JSON body
  (not exercised destructively here to avoid burning rate budget, but documented Crossref
  behaviour and consistent with the 200s observed on every valid call in this session).

## 3. Item metadata — the venue-class resolution table

**This section is the direct input to spec §6.2 and to Task 9.** Per `probe/RUBRIC.md`,
`venue_class` is classified from the item's own registered `type` + `container-title` +
`publisher` — never from the URL or the index that surfaced it. Crossref's registered `type`
is exactly that self-declared metadata, which is why the spec names Crossref authoritative
for this axis: **the classification signal Crossref returns is the same signal every other
connector's items must be checked against.**

### 3.1 Observed Crossref `type` values → venue class (all 12 queries + the C1 fixture)

| Crossref `type` observed | Occurrences (top results, 12 queries) | Also in C1 fixture (rows=5) | Mapped `venue_class` | Confidence |
|---|---|---|---|---|
| `journal-article` | Q7, Q9, C2 | — | `peer-reviewed-article` | High — direct, unambiguous when `container-title`/`publisher` present |
| `book-chapter` | Q1, Q4, Q6, Q10, C1 | 3 of 5 items | `book-chapter` | High — direct, per rubric "chapter within a larger work" |
| `book` | Q5 | — | `book` | High — direct, per rubric "book or monograph" |
| `posted-content` | Q8 | — | `preprint` | High — direct; DOI prefix `10.31219/osf.io` (OSF infrastructure) corroborates |
| `reference-entry` | Q2 | — | `book-chapter` (judgment call) | Medium — no dedicated class exists for encyclopedia entries; mapped to book-chapter because it has a `container-title` (the encyclopedia) and functions as a chapter, but this is an interpretation, not a direct rubric hit |
| `dataset` | Q3 | 2 of 5 items | `grey` (judgment call) | Low — verified via web search that this specific record is an APA PsycTherapy clinical-demonstration streaming video catalogue entry, not scholarly literature; `dataset` has no dedicated venue class and could equally be argued `unverified` |

Six distinct `type` values surfaced across 17 total items examined (12 top results + 5 C1
fixture items) — a narrower slice than Crossref's full registered-type vocabulary (which
also includes `monograph`, `report`, `dissertation`, `proceedings-article`,
`edited-book`, `standard`, `peer-review`, and others not observed in this benchmark).

### 3.2 Which venue classes Crossref can resolve from `type` alone, and which it cannot

**Reliably resolvable directly from registered `type`:**

- `peer-reviewed-article` — `type: journal-article` + non-null `container-title` (journal name) + `publisher`
- `book` — `type: book` or `monograph`, no `container-title`
- `book-chapter` — `type: book-chapter` (and, by judgment-call extension, `reference-entry`,
  `book-part`, `book-section`)
- `preprint` — `type: posted-content` (Crossref's dedicated preprint/working-paper wrapper;
  corroborated by OSF/arXiv-style DOI prefixes on posted-content records)
- `unverified` — the fallback path itself: no DOI, or a DOI with no registered type, is
  unambiguous and Crossref supports it natively (a missing-metadata state, not a lookup)

**Cannot be reliably resolved from `type` alone — this is the structural gap:**

- **`guideline`** — Crossref's controlled type vocabulary has **no dedicated guideline
  type**. A clinical-guideline document registers as `report`, `standard`,
  `journal-article`, or `other` depending entirely on how the issuing body chose to register
  it. Distinguishing a guideline from an ordinary report/article requires reading
  `publisher`/`container-title` and applying an editorial rule (e.g. "publisher is a named
  professional body AND type is report/standard"), which is exactly the paradigm-override
  judgment spec §6.2 explicitly reserves for Layer 4, not the envelope.
- **`institute-publication`** — same gap. Crossref has no "issued by a modality institute"
  type; `publisher` is a free-text field (e.g. "American Psychological Association (APA)"
  was observed on Q3, Q9, and C1's fixture rows), not a controlled institute/press
  distinction. A consumer would need a maintained allowlist of institute-publisher strings —
  which is precisely the "scraping URL strings for signal" pattern spec §6 was written to
  eliminate, just relocated to `publisher` strings instead of URLs.
- **`commentary`** — no dedicated type either. Editorials, letters, and commentaries
  routinely register as plain `journal-article`, indistinguishable by `type` from a full
  empirical article. Crossref does register `peer-review` as its own type (referee reports),
  which is adjacent but not what "commentary" means in this rubric (editorial/opinion
  content, not a review report).
- **`grey`** partially — `report`, `dissertation`, and `dataset` types exist and can anchor a
  `grey` classification, but (as Q3 demonstrates) `dataset` is heterogeneous enough that a
  clinical-demonstration video catalogue and an actual open research dataset both register
  identically as `type: dataset` — the distinction required a live web-search check, not
  something the registered metadata alone resolves.

**Net finding for §6.2 / Task 9**: Crossref reliably anchors 4 of the 9 venue classes
(`peer-reviewed-article`, `book`, `book-chapter`, `preprint`) plus the `unverified` fallback —
5 of 9 total. The remaining 4 (`guideline`, `institute-publication`, `commentary`, and fully
reliable `grey`) require an editorial-layer heuristic on top of Crossref's `publisher`/`type`
fields, not a direct `type` → class mapping. This matters directly for spec §6.2's claim that
venue classification is "resolved server-side from registered bibliographic metadata" —
that is true for just over half the taxonomy; the rest needs the Layer-4
paradigm-override layer spec §6.2 already anticipates, applied earlier and more broadly than
the spec text suggests.

### 3.3 Registry keys and envelope fields actually returned

Against spec §6.3's Literature Key Registry and §6.2's envelope fields, Crossref supplied,
across the 12 queries: `doi` (12/12), `type` (12/12), `publisher` (12/12), `venue` /
`container-title` (10/12 — absent for Q5's top-level book and Q8's posted-content, both of
which have no parent container by design), `isbn` (5/12, book/book-chapter items only),
`issn` (3/12, journal-article items only). `pmid`/`pmcid`/`openalex_id`/
`semantic_scholar_id`/`osf_id`/`arxiv_id` are never returned by Crossref — it is a
DOI-and-only-DOI registry by design; cross-connector ID reconciliation is the consuming
layer's job, not Crossref's. `oa_status` is not returned by `/works` at all (Crossref has a
separate, unrelated "license" block that is not an open-access status signal and was not
treated as one here).

### 3.4 Retraction status — how it is exposed, and what it costs to check

**Exposed via `update-to[]` on the work's own metadata record — no separate endpoint, no
extra request.** None of the 12 benchmark queries' top results happened to be retracted, so
this was verified with an independent live call rather than assumed:

```
GET /works?filter=update-type:retraction&rows=1
  → item.DOI = 10.1016/j.micpro.2020.103768
  → item.title = ["RETRACTED: Cross-Cultural communication of language learning ..."]
  → item.update-to = [{"DOI": "10.1016/j.micpro.2020.103768", "type": "retraction",
                        "label": "Retraction", "source": "publisher",
                        "updated": {"date-parts": [[2021,3,1]], ...}}]

GET /works/10.1016/j.micpro.2020.103768   (direct single-DOI lookup, not the filter route)
  → identical update-to block on the SAME record
```

The retraction notice is **not a separate linked work** the consumer must chase down — it is
a self-referencing block (`update-to[].DOI` equals the record's own `DOI`) attached directly
to the retracted article's own metadata. `type: "retraction"` is the operative signal;
`label`, `source` (`"publisher"` here — i.e. asserted by the publisher, not by Crossref
itself), and `updated` (the retraction date) ride along for free. `probe/connectors/crossref.py`'s
`_retraction()` helper already implements this correctly (checks `update-to[].type` for the
substring `"retract"`), validated against this live record.

**Cost: zero marginal requests.** `update-to` rides on the same response as every ordinary
search or single-DOI lookup — retraction status is a field read, not a second API call. There
is also a coarser discovery route, `filter=update-type:retraction`, for enumerating retracted
works in bulk (used above to find a live example), but per-item checking needs nothing beyond
what a normal `/works/{doi}` or search call already returns. This is the strongest structural
argument in this dossier for Crossref as the envelope's retraction-status source: the signal
is free, self-attached, and already-flowing through the adapter written for this probe.

A separate `relation` object also exists on work records (empty `{}` on the record checked
above) for broader is-cited-by/has-preprint/is-version-of style links; it was not needed for
retraction and is out of scope here.

## 4. Measured coverage — 12 cells

Full records: [`probe/results/crossref.json`](probe/results/crossref.json). All 12 pass
`probe.schema.validate`. Retrieved 2026-08-15 (~21:08–21:09 UTC).

| Query | Result | n_results | venue_class | Top result |
|---|---|---|---|---|
| Q1 IFS parts | hit | 9,204,356 | book-chapter | Unburdening Parts (2017), *IFS Therapy with Children* |
| Q2 Somatic Experiencing | hit | 469,967 | book-chapter | Somatic Experiencing (2015), SAGE Encyclopedia entry |
| Q3 AEDP transformance | partial | 1,104,654 | grey | AEDP (2023) — APA PsycTherapy demo-video dataset, not literature on transformance |
| Q4 Heroine's Journey | hit | 1,449,841 | book-chapter | The Heroine's Journey (2016), Murdock, *Encyclopedia of Psychology and Religion* |
| Q5 Marston 1928 DISC | hit | 1,485,266 | book | Emotions of Normal People (1928), Marston — the primary source itself |
| Q6 secure base/safe haven | partial | 1,399,165 | book-chapter | Training Partnerships (2012) — clinical-training dyads, not romantic dyads (verified) |
| Q7 Basson desire | hit | 3,718,455 | peer-reviewed-article | Basson, "hypoactive sexual desire disorder" (2010), *Menopause* |
| Q8 self-expansion + aesthetic | hit | 5,517,632 | preprint | Balzarini et al., Virtually Connected (2024), OSF posted-content |
| Q9 measurement invariance | hit | 3,112,525 | peer-reviewed-article | Positive Mental Health Scale invariance (2021), *Psychological Assessment* (`.supp` DOI) |
| Q10 working memory / fluid intelligence | hit | 2,762,709 | book-chapter | Individual Differences in Attention Control (2020), *Working Memory*, OUP |
| **C1** EFT couples (control) | hit | 9,525,294 | book-chapter | Love, Attachment Theory, and EFT Couples Therapy (2021), Routledge |
| **C2** fabricated construct (control) | **miss** (pass) | 11,218,320 | peer-reviewed-article | Glioblastoma/glycogen-metabolism article — adjacent-token match only, no construct match |

**Coverage score (Q1–Q10 only, per README): 8 hit / 2 partial / 0 miss.** C1 passes (not
counted). C2 passes as a clean negative — token-adjacent recall with no confident false
match on the fabricated "Neuro-Dynamic Co-Regulation Index" construct or its fabricated
citation.

Both `partial` calls (Q3, Q6) were independently verified against external sources
(web search against the publisher/APA database listings) rather than guessed from the title
alone — see `notes` in `probe/results/crossref.json` for the citations.

## 5. Fuzzy-to-Fact feasibility (ADR-001 §3)

**Yes, cleanly, on both halves.**

- **`search_works(query)` → ranked candidates**: exactly what `/works?query=` provides, and
  what this adapter's `search()` already implements. Crossref's relevance ranking is
  token/TF-IDF-style (evidenced by C2's adjacent-but-wrong-construct top hit and by every
  coverage query returning millions of `total-results` while the top 1–2 stayed on-topic) —
  useful for fuzzy discovery, not a semantic/citation-graph ranker like Semantic Scholar.
- **`get_work(doi)` strict lookup**: **verified live in this session**, not assumed —
  `GET https://api.crossref.org/works/10.1016/j.micpro.2020.103768` returned HTTP 200 with
  `message` as a single work object (not a list). This is the cleanest strict-lookup shape
  in the candidate set: the DOI **is** the primary key, Crossref **is** the DOI registration
  agency for the majority of scholarly DOIs, and the lookup needs no disambiguation logic —
  contrast an id-guessing or name-based strict lookup on a discovery-only index.
- DOI as lookup key: yes, natively and unambiguously — this is Crossref's actual data model,
  not an adapter convenience.

## 6. FastMCP wrapping feasibility (ADR-001 §2, §7)

- **Async-native REST**: yes. Plain HTTPS GET, JSON in/out, no session state, no SDK
  dependency — trivially wrappable with `httpx.AsyncClient` under FastMCP; no
  `run_in_executor` needed (the probe adapter itself uses stdlib `urllib` synchronously only
  because `probe/connectors/base.py` is deliberately minimal, per its own docstring — this is
  a probe-harness constraint, not a Crossref constraint).
- **Batch support**: no native multi-DOI batch endpoint (§2 above) — batch resolution of a
  DOI list means N sequential/concurrent single-work calls, each within the 3 req/s /
  3-concurrent polite-pool budget confirmed by this session's response headers. This is the
  one real friction point for wrapping: an agent handing over 50 DOIs to resolve cannot do
  it in one call the way OpenAlex's `filter=ids.openalex:ID1|ID2...` allows.
- **Rate limits under agent concurrency**: the observed `x-concurrency-limit: 3` header caps
  simultaneous in-flight requests from one polite-pool identity at 3 — a FastMCP wrapper
  serving multiple concurrent agent sessions against Crossref needs a shared limiter (the
  same `RateLimiter` pattern this probe already uses, scoped per-mailto-identity) rather than
  per-request-independent concurrency.
- **Slim mode expressible**: yes, trivially — spec §6.4's proposed slim triple (`doi`,
  `title`, `venue_class`) is a strict subset of every field this adapter already parses out
  of a Crossref record; no additional request or field is needed to support it.

## 7. Existing MCP server

Two independent unofficial Crossref MCP wrappers were found via web search; **no
Crossref-maintained official server exists.**

| Server | Maintainer | Transport | Auth | Tools | Status |
|---|---|---|---|---|---|
| `JackKuo666/Crossref-MCP-Server` (GitHub) | JackKuo666 (community) | stdio | keyless (email recommended, not required) | `search_works_by_query`, `get_work_metadata`, `search_journals`, `search_funders` | Minimally maintained — 3 commits, 7 stars, 5 forks, no dated recent activity visible |
| `@botanicastudios/crossref-mcp` (npm / Glama) | botanicastudios | remote-capable via `npx`, self-hostable | keyless, public Crossref API only | `searchByTitle`, `searchByAuthor`, `getWorkByDOI` | Glama lists it "D" maintenance grade, unclaimed by author, "–Maintainers"/"–Response time" — appears dormant |

Both are keyless thin wrappers over the same public `/works` endpoint this adapter calls
directly, with narrower tool surfaces than what §5–6 above show Crossref actually supports
(neither exposes retraction status, ISBN/ISSN extraction, or a documented rate-limit
strategy). Neither shows evidence of active maintenance as of this session (2026-08-15).

## 8. Recommendation: **wrap**

**Reasoning:**

1. Crossref is load-bearing infrastructure for this project's literature envelope (spec
   §6.2), not an optional coverage source — binding to a thin, dormantly-maintained
   community wrapper (§7) for a component the whole envelope's `venue_class` and retraction
   logic depends on is a fragility the design cannot absorb. A dropped or silently-broken
   third-party MCP server would degrade venue classification project-wide, not just one
   connector's coverage.
2. The wrapping cost is genuinely low (§6): keyless, stateless REST, async-native, DOI-keyed
   strict lookup already verified live, slim mode a free subset of parsed fields. There is no
   SDK-lock-in or sync-wrapper tax to justify binding instead.
3. Retraction status (§3.4) — the highest-value integrity signal in the whole envelope per
   spec §6.2 — is free on every call this project's own adapter already makes; wrapping keeps
   that signal a first-class citizen instead of something bolted onto someone else's tool
   schema.
4. §3.2's finding (Crossref anchors 5 of 9 venue classes directly; the other 4 need an
   editorial heuristic layer) is itself an argument for owning the wrapper: that heuristic
   layer has to live somewhere in `psychology-mcp`'s own envelope logic regardless of which
   connector supplies the raw metadata, and building it against a self-controlled adapter is
   more tractable than against an unofficial third party's fixed tool surface.

**Residual risk:**

- No native batch endpoint (§6) — a DOI-list resolution tool will cost N sequential/limited-
  concurrency calls, bounded by the observed `x-concurrency-limit: 3`. Acceptable for
  per-item retraction/venue checks; would need explicit rate-budget design if a Layer-2 tool
  ever needs to resolve hundreds of DOIs per request.
- The `guideline` / `institute-publication` / `commentary` gap (§3.2) is real and will
  recur for every connector, not just Crossref — `psychology-mcp`'s envelope needs an
  explicit publisher-string or modality-canon heuristic (Layer 4, per spec §6.2) for those
  three classes; Crossref's registered metadata alone will not close it.
- Rate-limit headers observed in this session (3 req/s, 3 concurrent) are runtime state, not
  a documented contractual guarantee — Crossref can and does vary polite-pool allowances;
  the wrapper should read `x-rate-limit-*` response headers at runtime rather than hardcode
  the value this session observed.
- `dataset`-typed records (Q3) demonstrated that `type` alone can silently include non-
  literature artefacts (clinical demonstration videos) that pass every schema check but are
  not scholarly literature — a wrapper should not assume "has a DOI and a type" is sufficient
  proof of citable literature without at least a coarse type-based filter.
