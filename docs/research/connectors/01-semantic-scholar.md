# 01 — Semantic Scholar

**Connector:** `semantic-scholar` · **API:** Semantic Scholar Academic Graph
**Probed:** 2026-08-15 unauthenticated (blocked) · **re-probed 2026-08-15 authenticated — §4 now MEASURED**

> **Read this first — this dossier was re-run.** The original pass fetched **zero** of
> twelve queries: the unauthenticated shared pool returned sustained HTTP 429 across three
> observation windows spanning ~1.5 hours. An API key was issued on 2026-08-15 and the
> **frozen, unchanged** benchmark was re-run authenticated. All twelve cells are now
> measured.
>
> The unauthenticated findings are retained rather than overwritten — they are the
> evidence for this connector being **credentialed rather than keyless**, which is a
> roster-level distinction the other three keyless connectors do not carry.

---

## 1. Identity and access

| | |
|---|---|
| Base | `https://api.semanticscholar.org/graph/v1/paper/search` |
| Auth | None *required*; an API key is optional but effectively necessary (below) |
| Key | Requested via `semanticscholar.org/product/api#api-key-form` |
| Format | JSON |

### The blocking finding: unauthenticated throughput is not usable for this benchmark

Semantic Scholar's unauthenticated tier shares **one 1000 req/s pool across every
unauthenticated user globally**, with a documented per-client ceiling of **100 requests
per 5 minutes**. Saturation is therefore driven by *other people's traffic*, and
self-pacing does not clear it.

Observed 2026-08-15, from two independent vantage points:

| Test | Result |
|---|---|
| Controller, isolated single call | HTTP 429 |
| Controller, 4 calls spaced 25s over 75s | HTTP 429 × 4 |
| Controller, 3 calls spaced 15s — **~1.5 h later, separate window** | HTTP 429 × 3 |
| **Authenticated**, single call | **HTTP 200** |
| **Authenticated**, 12-cell run at 1.2s spacing | **12 × HTTP 200** |
| **Authenticated**, detail pass at 1.3s spacing | **429 on the 2nd call** — see below |
| Harness run, `RATE = 10.0s` + retries at 20s / 40s / 70s | 429 on **cell 1**, all retries exhausted, run aborted |

The harness spent 130 seconds of deliberate backoff on the first query alone and never
got a 200. This is not a pacing defect on our side.

**Three separate observation windows across ~1.5 hours all returned 429.** One 200 was
obtained early in the first window (the C1 fixture, 21:15:38Z), so the pool clears
intermittently — but not reliably, and not on any schedule a client can plan around.

**An API key was requested and is pending.** Semantic Scholar's acknowledgement states
that requests are prioritised for *"academic and research institutions, nonprofit
organizations, and government entities"*, with no timeline, and adds that *"most
endpoints are available to you as an unauthenticated user, with a lower rate limit."*
**That last claim did not hold under measurement**: the unauthenticated tier is not
merely slower, it failed to complete a single one of twelve queries across three windows.
A wrapper cannot be built against a tier whose availability is this variable.

**Consequence:** Semantic Scholar is a **credentialed connector**. OpenAlex, Crossref and
Europe PMC each completed all twelve queries keyless in the same session. This one could
not complete one.

### Terms and attribution — VERIFIED on key issuance

**Attribution is a licence obligation, not a courtesy.** The issuing terms require
attribution to Semantic Scholar, or citation of *The Semantic Scholar Open Data
Platform*, in any published material using its results.

This propagates: a dissertation or report grounded through this connector inherits the
obligation. It is now a Required Pattern in the `psychology-mcp` constitution (v1.1.0)
rather than a client-level detail, because the consumer of a grounded claim — not the
client that fetched it — is where the obligation lands.

## 2. Mechanics

Response envelope, confirmed from the captured fixture:

```json
{ "total": 16523, "offset": 0, "next": 5, "data": [ … ] }
```

- **Pagination** — `offset` / `limit`, with `next` supplying the following offset. Simple
  offset paging, no cursor.
- **Projection** — `fields` is a comma-separated allowlist and is mandatory in practice;
  omitting it returns a minimal stub. The probe used
  `title,year,authors,externalIds,venue,publicationTypes,publicationVenue,openAccessPdf`.
- **Errors** — 429 returns a JSON body with `message` and `code`, not an empty response.

### A parser trap worth recording

`openAccessPdf` is **present and non-null even on closed-access records**, carrying
`status: "CLOSED"` and an empty `url`. Testing the object's truthiness — the obvious
implementation, and the one this project's own draft parser used — mislabels closed
articles as open access. The correct read is the nested `status` field. Observed values
in the C1 sample: `GREEN`, `CLOSED`.

## 3. Item metadata

**This is Semantic Scholar's strongest section**, and it is fully evidenced by the
captured fixture.

Per-record fields observed across the five C1 results:

| Registry key | Source field | Observed |
|---|---|---|
| `doi` | `externalIds.DOI` | 3 of 5 |
| `pmid` | `externalIds.PubMed` | 3 of 5 |
| `pmcid` | `externalIds.PubMedCentral` | 0 of 5 (field supported) |
| `semantic_scholar_id` | `paperId` / `externalIds.CorpusId` | **5 of 5** |
| `arxiv_id` | `externalIds.ArXiv` | 0 of 5 (field supported) |
| `issn` | `publicationVenue.issn` | 3 of 5 |
| `isbn` | — | not supplied |

| Envelope field | Source field | Observed |
|---|---|---|
| `type` | `publicationTypes[]` | 5 of 5 — values `JournalArticle`, `Review`, `ClinicalTrial` |
| `venue` | `venue` / `publicationVenue.name` | 3 of 5 |
| `publisher` | `publicationVenue.publisher` | **0 of 5 — null on every record** |
| `oa_status` | `openAccessPdf.status` | 3 of 5 |
| `retraction_status` | — | **not supplied** |

Also carries `MAG` (Microsoft Academic Graph) ids, which are outside the registry.

### Three findings that bear on the envelope design

**(a) Richest identifier crosswalk in the candidate set.** A single call returns DOI +
PubMed id + a stable corpus id + ISSN together. No other probed connector supplies that
crosswalk in one response, which makes S2 unusually well suited to the triangulation
role (ADR-001 §6).

**(b) `publisher` is never supplied.** Venue-class resolution that depends on publisher —
`institute-publication` most of all, since it is defined by *who* published rather than
*what type* the item is — cannot be performed from S2 metadata alone.

**(c) Registered type present without a DOI.** 2 of 5 records carry
`publicationTypes: ['Review']` but no DOI (only `CorpusId`, and in one case `MAG`).
Under the design's current resolution order — *no DOI → `unverified`* — those records are
untierable despite the API having told us what they are. Europe PMC exhibits the same
pattern independently, so this is a recurring class, not a per-connector quirk.

## 4. Measured coverage — 5 hit / 4 partial / 1 miss

**All 12 cells fetched authenticated, 2026-08-15.** Frozen benchmark, unchanged.

| Query | Result | n | Top result | venue_class |
|---|---|---:|---|---|
| Q1 IFS | **hit** | 49 | *Internal Family Systems Therapy* — Blatner | peer-reviewed-article |
| Q2 Somatic/Sensorimotor | partial | 5 | *Regulating Trauma Through the Body* (narrative review) | peer-reviewed-article |
| Q3 AEDP transformance | **hit** | 110 | ***AEDP: Transformance In Action* — D. Fosha, 2011** | **unverified** |
| Q4 Heroine's Journey | partial | 5 | Heroine's Journey in Italian TV serials | unverified |
| Q5 Marston DISC 1928 | partial | 1 | *Comparative Study of MBTI and DISC* | unverified |
| Q6 secure base, established dyads | partial | 116 | Secure base/safe haven in adult **child-parent** dyads | peer-reviewed-article |
| Q7 Basson responsive desire | **hit** | 235 | Basson, *Women's sexual desire — disordered or misunderstood?* | peer-reviewed-article |
| Q8 novelty + aesthetic engagement | miss | 7 | Lymphangioleiomyomatosis physical activity | peer-reviewed-article |
| Q9 measurement invariance | **hit** | 40,856 | DERS-SF psychometric validation | peer-reviewed-article |
| Q10 working memory / Gf | **hit** | 2,117 | Unsworth et al. | peer-reviewed-article |
| C1 *positive control* | **hit** | 16,523 | 'Hold me Tight' EFT RCT | peer-reviewed-article |
| C2 *negative control* | miss ✓ | 1 | Mouse Nrf2 SUMO-binding study | unverified |

**Second-best measured coverage in the candidate set**, behind Crossref's 8/2/0.

### 4.1 Q3 — the gap no other connector closed

`00-coverage-matrix.md` §9 recorded *"AEDP / transformance (Q3) — no hit anywhere. The one
query the entire candidate set fails."* **Semantic Scholar returned Fosha's own paper,
*AEDP: Transformance In Action* (2011).**

That finding is now superseded, and the correction matters more than the win: Q3 was the
sharpest evidence that modality-theory literature was unreachable. It was reachable — by
the one connector we could not measure.

### 4.2 The Q3 record carries neither a DOI nor a type

The single most valuable result in this run resolves to `venue_class: unverified`,
`classification_basis: none`. Semantic Scholar returned a `CorpusId` and nothing else —
no DOI, no `publicationTypes`, no venue.

**So the connector that alone can find AEDP theory cannot say what kind of thing it
found.** A consumer requiring `registered` basis would discard it; one accepting
`index-asserted` still gets nothing, because there is no asserted type either. This is
the strongest concrete argument in the whole benchmark for `classification_basis` being a
distinct field rather than collapsed into `venue_class`.

### 4.3 Partials are all real discriminations, not near-misses

- **Q6** returned secure-base/safe-haven research in adult **child-parent** dyads. Q6 is
  scoped to *established adult romantic* dyads precisely to preserve that distinction.
- **Q5** found the DISC model but via an MBTI comparison, not Marston's 1928 primary.
- **Q4** found the Heroine's Journey applied to Italian television serials, not clinical
  or narrative-psychology use.

Each is the query doing its job.

### 4.4 Authenticated rate limit is tighter than nominal

The granted limit is **1 request/second cumulative across all endpoints**, with the
issuer's instruction to pace *below* it. MEASURED: the 12-cell run at 1.2s spacing
completed cleanly, but a follow-up detail pass at **1.3s spacing drew a 429 on its second
call**. Sustained sequential use needed **2.5s**.

That is a real constraint on any gateway built here, independent of coverage — roughly
24 works/minute, and cumulative across endpoints means search and fetch share the budget.

## 5. Fuzzy-to-Fact feasibility (ADR-001 §3)

**Phase 1 (fuzzy).** `/paper/search` accepts natural language and returns ranked
candidates with a `total`. Confirmed by the fixture — the C1 query's top result is the
on-target paper, so relevance ranking is genuine rather than token soup.

**Phase 2 (strict).** Documented as `/paper/{ID}` with typed ID prefixes — `DOI:`,
`CorpusId:`, `PMID:`, `ARXIV:`, `MAG:`. **Not verified live**, because every call in the
probe window returned 429. Recorded as documented-but-unverified.

If it behaves as documented, the two-tool pattern maps cleanly, and S2 is unusual in
accepting *several* CURIE-shaped prefixes rather than only a DOI — useful for records
that lack a DOI, which §3(c) shows are common.

## 6. FastMCP wrapping feasibility (ADR-001 §2, §7)

- **Async** — plain REST/JSON over HTTPS; a straight `httpx` async client. No SDK, so no
  `run_in_executor` exception needed (ADR-001 §2).
- **Slim mode (§7)** — `fields` is a ready-made projection mechanism. The
  `doi`/`title`/`venue_class` slim triple maps to `fields=externalIds,title,publicationTypes`.
  Better native support than any other probed connector.
- **Batch** — a `/paper/batch` POST endpoint is documented; not verified here.
- **Dominant wrapping cost is rate limiting, not shape.** A wrapper must hold an API key,
  honour `Retry-After`, and degrade predictably under 429 rather than raising. The
  adapter written for this probe already retries 20s/40s/70s and still could not land a
  single call unauthenticated — a production wrapper needs the key, not better backoff.

## 7. Existing MCP servers

Several community implementations exist; **none is official or Semantic
Scholar–maintained**, and none was verified live here:

- `hamid-vakilzadeh/AIRA-SemanticScholar`
- `JackKuo666/semanticscholar-MCP-Server`
- `alperenkocyigit/semantic-scholar-graph-api`
- `FujishigeTemma/semantic-scholar-mcp`
- listings on Glama and MCP Market

All are unaffiliated third parties. Binding one would place a community-maintained server
in the path of the plugin's primary non-PubMed literature route — and would still not
solve the rate limit, which belongs to the upstream API rather than to any wrapper.

## 8. Recommendation — WRAP. Tier 1, not Tier 0.

**Wrap in `psychology-mcp` as a credentialed connector. Do not bind a third-party server.**

The conditional in the earlier revision is discharged: coverage is now measured at
**5 hit / 4 partial / 1 miss**, second only to Crossref.

### Why Tier 1 rather than Tier 0

Tier 0 is Crossref + OpenAlex because the envelope is not implementable without both —
Crossref classifies, OpenAlex clears retraction. **Semantic Scholar does neither.** It
supplies no `publisher` (0/12) and no retraction signal (0/12), so it cannot carry either
Tier-0 responsibility. Its coverage is excellent and its unique reach is real, but
coverage is not what Tier 0 is for.

### What it uniquely brings

1. **Q3 — AEDP transformance.** The only connector in the candidate set to answer it,
   returning Fosha's own *AEDP: Transformance In Action* (2011). This was recorded as the
   one query the entire set failed.
2. **Records with no DOI.** 3 of 12 top results carry only a `CorpusId`. Its multi-prefix
   strict lookup (`CorpusId:`, `PMID:`, `ARXIV:`, `MAG:`) is the only route to them.
3. **Identifier crosswalk.** DOI + PMID + PMCID + CorpusId + ISSN in one response.

### The cost, stated plainly

- **Credentialed.** The other three roster connectors completed keyless. This one is
  unusable without a key: zero of twelve across three unauthenticated windows.
- **1 req/s cumulative across all endpoints** — and MEASURED tighter than nominal, with a
  429 at 1.3s spacing and 2.5s needed for sustained use. Roughly 24 works/minute, shared
  between search and fetch. That constrains any gateway built on it regardless of
  coverage, and §6b's caching guidance is the mitigation: its contributions are all
  low-volatility and cache indefinitely.
- **Attribution is a licence obligation** (§1) that propagates to every downstream
  consumer of a grounded claim.
- **Cannot classify its own best result.** Q3 returned no DOI, no type, no venue — so the
  hit that justifies this connector arrives as `venue_class: unverified`,
  `classification_basis: none`.

### Residual risks

- **`publisher` never supplied** — 0/12, confirming the fixture. Venue classification
  depending on publisher must come from Crossref or OpenAlex.
- **No retraction signal** — a record sourced only from S2 is `retraction_status: unknown`,
  never `not-retracted`.
- **Batch endpoint still unverified.** `/paper/batch` is documented; the 1 req/s ceiling
  makes verifying it worthwhile, since batch is the only way to beat the per-call budget.
- **Strict lookup still unverified live** — §5 rests on documentation.
