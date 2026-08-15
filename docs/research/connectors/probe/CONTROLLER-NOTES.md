# Controller notes — cross-connector findings

Observations made while verifying per-connector deliverables that **no single dossier
could see**, because each agent saw only its own connector. Task 8 (coverage matrix)
must reconcile these; Task 9 (literature envelope) consumes some of them.

Written by the controller during verification, not by the per-connector agents.

---

## 1. `n_results` is NOT comparable across connectors

| Connector | min | max |
|---|---:|---:|
| OpenAlex | 7 | 53,884 |
| Crossref | 469,967 | 11,218,320 |

Three orders of magnitude apart, because the two APIs mean different things by a
result count. Crossref's `query=` is a loose OR match across the whole ~160M-record
registry, so `total-results` approximates "records containing any of these tokens".
OpenAlex's `search=` is a full-text token match over a smaller indexed corpus.

**Consequence for Task 8:** `n_results` must NOT appear as a comparable column, and
no connector may be ranked by it. Report it **per connector** as a within-connector
signal only (e.g. "this query returned far fewer records than that one, for this
connector"), and say plainly in the matrix that cross-connector count comparison is
invalid. A reader who sees 9,204,356 beside 10,134 will otherwise conclude Crossref
has 900× the coverage, which is false.

The comparable columns are `result`, `venue_class`, and `metadata_completeness`.

---

## 2. `venue_class` / `result` orthogonality

Surfaced by the OpenAlex run; ratified into `RUBRIC.md` and sent to the four
then-in-flight agents. `venue_class` classifies the top result **regardless of
relevance**; `unverified` means "no DOI or no registered type", never "missed".

Crossref confirmed on request that its records already followed this convention, so
no back-edit was needed there.

**Consequence for Task 8:** the `venue_class` column is comparable, but for `miss`
rows it describes an off-topic artefact. Present `result` and `venue_class` as
separate axes; never collapse them into a single quality score.

---

## 3. Q5 resolved — a predicted risk that did not materialise

Spec §10 risk table: *"Q5 (1928 primary source) resolves in none of the five —
expected. Internet Archive / Open Library revisited in a second pass."*

Crossref returned **"Emotions of normal people." — William Moulton Marston — 1928**,
`venue_class: book`. The historical-primary format axis is therefore covered by a
selected connector, and the Internet Archive / Open Library second pass named in
spec §3.5 is **not** required on Q5's account.

Record this in `DECISION.md` rather than silently dropping the deferred candidate.

---

## 4. Open judgement call — Crossref Q9

Crossref's Q9 top result is *"Supplemental Material for Positive Mental Health Scale:
Validation and Measurement Invariance Across Eight Countries"* — scored `hit`.

It is a **supplemental-material record**, not the article itself. Defensible as a hit
(it is genuinely that literature), but another agent facing the same case might score
`partial`. Left as the agent recorded it rather than overridden, because inconsistently
overriding one connector's judgement is worse than a noted borderline.

**Task 8 should surface it as a borderline call**, not silently average it.

---

## 5. C1 as a harness check is invalid for a non-index connector

`RUBRIC.md` states: *"C1 expected `hit` for every connector. A miss means a broken
client."* **PsyArXiv/OSF returned `miss` on C1 — and the client is not broken.**

Independently verified by the controller with direct `curl` calls outside the harness:

| Request | Result |
|---|---|
| `filter[title]=couples` | **73** hits |
| `filter[title]=couples therapy` | **0** |
| `filter[title]=<full C1 query>` | **0** |

`filter[title]` is a contiguous case-insensitive **substring** match on the title
field. No multi-word natural-language query occurs verbatim in a title, so every
benchmark query misses regardless of what PsyArXiv actually holds.

**The rubric's premise was wrong**, not the agent's result. C1 validates a harness only
when the connector offers relevance-ranked search. For a retrieval-by-identifier or
substring API, a C1 miss is a *search-surface finding*, not a client fault.

**Consequence for Task 8:** do not report OSF's 0/12 as "worst coverage". It did not
lose a coverage contest; it was never in one. Report it as a connector whose search
surface cannot express the benchmark at all — which is the actual, and more useful,
finding.

**Consequence for the rubric** (recorded, not retro-applied): C1's diagnostic power is
conditional on the connector being an index.

---

## 6. Preprint DOIs may carry the PUBLISHED article's registered type

Reported by the PsyArXiv/OSF agent, **partially corroborated** by the controller.

Agent's finding: on a *published* PsyArXiv preprint, `attributes.doi` holds the
**published journal article's** DOI rather than an OSF-minted preprint DOI
(`preprint_doi_created` was null). Crossref therefore classifies all five checked DOIs
as `journal-article`, not `posted-content`. Two of the five carry a
`relation.has-preprint` back-reference to the real `10.31234/osf.io/...` DOI, proving
the records are distinct.

Controller spot-check: sampled five PsyArXiv records independently and found
`doi: None` and `preprint_doi_created: None` on all five — so **many OSF records carry
no DOI at all** (which is why all 12 cells are `venue_class: unverified`). This
corroborates the DOI-sparsity half. The claim about what a *populated* DOI points at is
the agent's, from five records; not independently re-verified here.

**Consequence for Task 9 — this is first-order.** The proposed envelope resolution
order is *"DOI with registered metadata → classify from the item's own registered
type."* If a preprint record's DOI resolves to the published article, that rule
classifies a preprint as `peer-reviewed-article`. The envelope needs either a
provenance-beats-DOI rule for repository-sourced records, or an explicit
`relation.has-preprint` check. Do not let §6.2 ship without addressing it.

---

## 7. "No DOI → `unverified`" discards registered type that IS present

Surfaced while reconciling Europe PMC's miss rows.

Europe PMC's Q2 top result carries a **registered `pubType` of `review-article`** but
**no DOI**. Spec §6.2's resolution order is:

1. DOI with registered metadata → classify from the item's own registered type
2. No DOI → `unverified`
3. Neither → `unverified`

Applied literally — which the agent did, correctly — Q2 lands at `unverified` even
though the API told us what kind of thing it is. The same happened on C2 (no DOI,
`pubType` present but malformed: the literal string `"Abstract"`).

**This is a genuine design question for Task 9, not an error.** The resolution order
treats the DOI as the *anchor of trust*, so type without a DOI is discarded. That is
defensible — an unregistered type is an assertion by the index rather than by a
registration authority — but it is a decision the spec makes implicitly and never
argues for. §6.2 should either:

- **defend it explicitly** (registered-with-Crossref/DataCite is the trust boundary; an
  index's self-reported type is not equivalent), or
- **add a tier** distinguishing "registered type" from "index-asserted type", so a
  no-DOI record with a usable type is not flattened into the same bucket as a record
  with no type information at all.

The distinction is not cosmetic: it changes how much of Europe PMC's PMC-sourced
content (11% of its sampled results, frequently DOI-less) can be tiered at all.

---

## 8. Semantic Scholar throttles unauthenticated — a class difference, not a hiccup

Controller-verified independently: a single-result unauthenticated call to
`api.semanticscholar.org/graph/v1/paper/search` returned **HTTP 429**, body
*"Too Many Requests. Please wait and try again or apply for a key for higher rate
limits."*

OpenAlex, Crossref, and Europe PMC each completed all 12 queries **keyless**.
Semantic Scholar could not.

**Consequence for `DECISION.md` §7.2.** This splits the candidate set along the axis
AGE-548 question 3 is actually about. Keyless connectors can be declared in
`.mcp.json` with nothing further. A credentialed connector is still declarable —
`${VAR}` header expansion, `headersHelper`, or plugin `userConfig` with
`sensitive: true` — but it obliges the consumer to obtain and supply a key, which is a
real adoption cost and a different scope answer. Do not let the roster present
Semantic Scholar as equivalent-but-slower.

---

## 9. `publisher` is not universally available — Crossref may be the only source

From the Semantic Scholar C1 fixture: `publicationVenue.publisher` is **`None` on every
one of the five records**, while `venue` and `issn` are populated. Europe PMC likewise
returns `journalTitle` but no publisher field.

Spec §6.2 classifies venue class from *"the item's own registered `type`, venue, and
publisher"*. If publisher is only reliably available from Crossref, then either:

- the classifier must work from `type` + venue alone for non-Crossref sources, or
- Crossref becomes a mandatory second lookup for any DOI-bearing record — which
  contradicts the "zero marginal cost" retraction finding only insofar as it applies to
  *records Crossref already returned*, not to records surfaced by another connector.

`institute-publication` is the class most dependent on publisher (it is defined by *who
published it*, not what type it is). That class was already flagged unresolvable from
Crossref's `type` vocabulary alone; this note says it may be unresolvable from any
connector's metadata without a publisher-string heuristic at Layer 4.

---

## 10. Type present without a DOI recurs across connectors — it is not a Europe PMC quirk

Note §7 recorded this for Europe PMC's Q2. The Semantic Scholar fixture shows the same
shape independently: **2 of 5 C1 records carry no DOI** (only `CorpusId`, and in one case
`MAG`) while still carrying `publicationTypes: ['Review']`.

So the "registered type present, DOI absent" case is not an artefact of one connector's
indexing. It is a recurring class that §6.2's resolution order currently flattens to
`unverified`. Task 9 should size it: on the evidence so far it is roughly 11% of Europe
PMC's sampled results and 40% of the S2 C1 sample.

---

## 11. Semantic Scholar has NO measured coverage — absence of measurement, not measured absence

`probe/results/semantic-scholar.json` is `[]`. Zero of twelve cells were fetched. The
run aborted on cell 1 after exhausting 20s/40s/70s of backoff against sustained 429s,
independently reproduced by the controller with four spaced isolated calls.

**Task 8 must not render this as `0/10`.** Four connectors have measured coverage; this
one has none. Presenting an empty result in the same column as a measured zero would
state something false — and would rank the plugin's own *designated* non-PubMed source
last on evidence that does not exist.

Render it as a distinct state — `not measured (429)` — in every table, and keep it out
of any coverage tally, ranking, or aggregate.

The single datum that exists is the C1 fixture (`total: 16523`, on-target top result,
DOI `10.1111/famp.12305`), captured before the pool saturated. It is one observation,
not a scored cell, and it is counted nowhere.

**Consequence for `DECISION.md`:** the roster entry for Semantic Scholar is provisional.
Its §8 is a *conditional* wrap resting on metadata quality and the plugin's declared
intent, not on measured coverage. If the roster needs a defensible ordering, the honest
move is a keyed re-run — the twelve queries are frozen, so a later run is directly
comparable.

---

## 12. Crossref rate limit was initially exceeded

The Crossref agent found, from live `x-rate-limit-*` response headers, that the
adapter's initial `RATE = 0.2` (5 req/s) was above Crossref's declared 3 req/s cap,
and tightened it to `0.35` after the run. No 429s were observed, but the recorded
cells were fetched slightly over-rate.

Not a data-integrity problem — the responses are genuine and the counts stand. Worth
noting in `DECISION.md` §7.1 as an argument for reading `x-rate-limit-*` headers at
runtime rather than hardcoding a rate, which is already in that dossier's §8 residual
risks.
