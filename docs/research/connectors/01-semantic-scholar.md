# 01 — Semantic Scholar

**Connector:** `semantic-scholar` · **API:** Semantic Scholar Academic Graph
**Probed:** 2026-08-15 · **Status: §4 coverage BLOCKED — see below**

> **Read this first.** Zero of the twelve benchmark queries were fetched through the
> harness. The unauthenticated API returned sustained HTTP 429 throughout the probe
> window. `probe/results/semantic-scholar.json` is therefore `[]` — an empty array, not
> twelve zero-result rows. Nothing in this dossier describes a response that was not
> received.
>
> One genuine C1 response **was** captured earlier in the window and is preserved as
> `probe/fixtures/semantic-scholar-C1.json`. Sections 1, 2, 3, 5, 6, 7 and 8 are written
> from that payload plus published documentation. Section 4 is not written, because it
> cannot be.

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
| Harness run, `RATE = 10.0s` + retries at 20s / 40s / 70s | 429 on **cell 1**, all retries exhausted, run aborted |

The harness spent 130 seconds of deliberate backoff on the first query alone and never
got a 200. This is not a pacing defect on our side.

**Consequence:** Semantic Scholar is a **credentialed connector**. OpenAlex, Crossref and
Europe PMC each completed all twelve queries keyless in the same session. This one could
not complete one.

### Terms and attribution

Not verified. The published API terms were not retrieved during this probe and no
attribution requirement is asserted here. This must be established before any binding
decision is finalised — the sibling PubMed connector already carries a DOI-link
attribution obligation, so per-source obligations should be assumed until checked.

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

## 4. Measured coverage — BLOCKED, NOT MEASURED

**Cells recorded: 0 of 12.** `probe/results/semantic-scholar.json` is `[]`.

Per-query status is **not uniform**, and the distinction matters — "attempted and
throttled" is a different claim from "never attempted". Full receipt:
`probe/results/semantic-scholar-fetch-log.json`.

| Query | Status | Detail |
|---|---|---|
| C1 | **fetched, not scored** | One genuine 200 (`total: 16523`) captured as the fixture. Not recorded as a cell — a single observation outside a completed run is not a scored result |
| Q1 | attempted, **429** | 1 initial + 3 retries (20s/40s/70s) exhausted |
| Q2 | attempted, **429** | 1 initial + 3 retries exhausted |
| Q3 | interrupted | Request in flight when the run was stopped; no partial recorded |
| Q4–Q10, C2 | **not attempted** | Run stopped before reaching them |

Approximately 14 real HTTP calls were made against the API across all attempts,
including retries and fixture captures. A separate controller-run harness invocation
independently aborted on Q1 after the same 130s of backoff, and four isolated controller
calls spaced over 75s all returned 429.

No coverage figure is reported, estimated, or inferred. This connector must not appear
in the coverage matrix as `0/10` — that would read as measured absence of coverage rather
than absence of measurement, and would rank the plugin's own designated non-PubMed source
last on evidence that does not exist. Render it as **`not measured (429)`**.

**To complete this section:** obtain an API key, set it as a request header in the
adapter, and re-run `python3 -m probe.run --connector semantic-scholar`. The twelve
queries are frozen and unchanged, so a later run is directly comparable with the other
four connectors.

The one datum that exists: the C1 query returned `total: 16523` with a well-targeted top
result (*"Effectiveness of the 'Hold me Tight' Relationship Enhancement Program"*, 2018,
*Family Process*, DOI `10.1111/famp.12305`) at the time the fixture was captured. That is
a single observation, not a scored cell, and it is not counted anywhere.

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

## 8. Recommendation — CONDITIONAL WRAP, pending a keyed re-run

**Wrap, conditional on obtaining an API key. Do not bind a third-party server.**

Reasoning:

1. **Metadata quality is best-in-class** (§3). The DOI + PMID + CorpusId + ISSN crosswalk
   in one response directly serves ADR-001 §6 triangulation, and `fields` gives native
   slim mode.
2. **The plugin already names Semantic Scholar** as its intended non-PubMed literature
   binding, in `CONNECTORS.md`, `SKILL.md` (twice) and `modality-canon.md`. It is the
   designated source for exactly the modality and book-canon literature the other
   connectors were weakest on.
3. **Binding a community server helps nothing** — the constraint is upstream.

**The honest caveat, and it is load-bearing: coverage was never measured.** This
recommendation rests on metadata quality and on the plugin's own declared intent — *not*
on evidence that Semantic Scholar answers the twelve benchmark queries better than
OpenAlex or Crossref. That evidence does not exist yet. It must not be presented as
though it does.

### Residual risks

- **Coverage unmeasured** — the recommendation is provisional until a keyed re-run fills §4.
- **Credentialed, unlike its peers** — three other connectors work keyless. A key imposes
  acquisition, storage and rotation cost on every consumer. Declarable via `${VAR}` header
  expansion, `headersHelper`, or plugin `userConfig` with `sensitive: true`, but it is a
  different consumer contract and belongs in the scope-boundary decision.
- **Even keyed, 100 req/5 min is modest** — fine for interactive research, thin for batch.
- **No publisher, no retraction status** — both must come from elsewhere (Crossref supplies
  both).
- **Terms of use unverified** — attribution obligations unknown.
- **Strict lookup unverified** — §5 rests on documentation.
