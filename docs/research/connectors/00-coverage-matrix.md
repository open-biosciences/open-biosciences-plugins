# 00 — Coverage matrix

**Probed:** 2026-08-15 · **Benchmark:** frozen 2026-08-15, see [`README.md`](README.md)
**Cells:** 60 recorded, 0 invalid — **all five connectors measured** · **Source of truth:** `probe/results/*.json`

Every figure here is counted from the recorded cell records, not from any agent's
summary. That distinction caught at least one arithmetic error — see *Corrections*.

---

## 1. The matrix

`result` for each connector × query. **Read this table alongside §2 — `result` alone
does not rank connectors, and `n_results` is deliberately absent (§6).**

| | Semantic Scholar | OpenAlex | Crossref | Europe PMC | PsyArXiv/OSF |
|---|---|---|---|---|---|
| **Q1** IFS | **hit** | miss | **hit** | miss | miss |
| **Q2** Somatic/Sensorimotor | partial | partial | **hit** | miss | miss |
| **Q3** AEDP transformance | **hit** | partial | partial | miss | miss |
| **Q4** Heroine's Journey | partial | miss | **hit** | miss | miss |
| **Q5** Marston DISC 1928 | partial | partial | **hit** | miss | miss |
| **Q6** secure base, established dyads | partial | partial | partial | partial | miss |
| **Q7** Basson responsive desire | **hit** | **hit** | **hit** | partial | miss |
| **Q8** novelty + aesthetic engagement | miss | miss | **hit** | miss | miss |
| **Q9** measurement invariance | **hit** | partial | **hit** | **hit** | miss |
| **Q10** working memory / Gf | **hit** | **hit** | **hit** | **hit** | miss |
| **C1** *positive control* | **hit** | **hit** | **hit** | **hit** | miss |
| **C2** *negative control* | miss ✓ | miss ✓ | miss ✓ | miss ✓ | miss ✓ |

### Coverage tallies — Q1–Q10 only, controls excluded

| Connector | hit | partial | miss | Measured? |
|---|---:|---:|---:|---|
| **Crossref** | **8** | 2 | 0 | ✅ 10/10 |
| **Semantic Scholar** | **5** | 4 | 1 | ✅ 10/10 *(requires an API key)* |
| **OpenAlex** | 2 | 5 | 3 | ✅ 10/10 |
| **Europe PMC** | 2 | 2 | 6 | ✅ 10/10 |
| **PsyArXiv/OSF** | 0 | 0 | 10 | ✅ 10/10 |

## 2. Two results that are not what they look like

**Semantic Scholar was re-run with an API key.** The original pass recorded zero cells —
the unauthenticated shared pool returned sustained 429 across three windows. A key was
issued 2026-08-15 and the **frozen, unchanged** benchmark was re-run: 5 hit / 4 partial /
1 miss. It is the only connector requiring credentials; the other four completed keyless,
and that distinction is a roster fact, not a footnote. See
[`01-semantic-scholar.md`](01-semantic-scholar.md) §4.

**PsyArXiv/OSF's 0/10 is not a coverage contest it lost.** OSF's `filter[title]` is a
contiguous case-insensitive **substring** match on titles only — not an index. The
controller verified directly: `filter[title]=couples` returns 73 hits;
`filter[title]=couples therapy` returns 0. No multi-word natural-language query occurs
verbatim in a title, so every benchmark query misses regardless of what PsyArXiv holds.
The finding is *"this connector cannot express the benchmark"*, which is more useful than
a score.

## 3. Controls

**C1 (positive)** — `hit` for all four connectors that could reach it. The harness is
sound. OSF's C1 miss is the §2 search-surface finding, not a broken client; the rubric's
premise that *"a C1 miss means a broken client"* holds only for relevance-ranked indexes.

**C2 (negative)** — **passed on all five.** No connector returned a result presented as
matching the fabricated construct *"Neuro-Dynamic Co-Regulation Index (Vanderbilt & Hayes
2019)"*. Three returned topically adjacent papers via token matching and were scored
`miss` with the required note — Crossref's top adjacent result was a glioblastoma /
glycogen-metabolism article matching only on *"regulation"* and *"Hayes"*. No connector
fabricated a match. Given that fabricated citations have previously reached a user-facing
surface in this ecosystem, this is a meaningful negative.

## 4. Coverage by format axis

The axis that motivated the whole effort — can a connector reach non-journal literature.

| Format axis | Query | Only connector to hit |
|---|---|---|
| **Monograph / book canon** | Q4 Heroine's Journey | **Crossref** — returned *The Heroine's Journey*, Maureen Murdock, 2016 |
| **Historical primary** | Q5 Marston 1928 | **Crossref** — returned *"Emotions of normal people."*, William Moulton Marston, **1928** |
| Contemporary clinical | Q1–Q3 | Crossref (Q1, Q2); nobody on Q3 |
| Empirical journal | Q6–Q10 | Crossref 4/5, OpenAlex 2/5, Europe PMC 2/5 |

**Q5 falsifies a spec prediction.** Spec §10 risk table: *"Q5 (1928 primary source)
resolves in none of the five — expected. Internet Archive / Open Library revisited in a
second pass."* Crossref resolved it. The deferred Internet Archive candidate is **not
required on Q5's account**.

**Q3 (AEDP transformance) is the only query no connector hits.** Crossref's best is a
`partial` — an APA PsycTherapy clinical-demonstration *video* catalogue entry, typed
`dataset`, not literature on transformance. This is the sharpest remaining gap.

## 5. Coverage by subject axis

| Subject axis | Queries | Crossref | OpenAlex | Europe PMC |
|---|---|---|---|---|
| Clinical / psychotherapy | Q1–Q3 | 2 hit, 1 partial | 2 partial, 1 miss | 3 miss |
| Narrative / historical | Q4–Q5 | **2 hit** | 1 partial, 1 miss | 2 miss |
| Relational / sexology / social | Q6–Q8 | 2 hit, 1 partial | 1 hit, 2 partial | 2 partial, 1 miss |
| **Quantitative / cognitive** | Q9–Q10 | 2 hit | 1 hit, 1 partial | **2 hit** |

**Q9–Q10 justified their late addition.** They were added during spec design to close a
subject-axis blind spot, and they are the **only** queries Europe PMC hits. Without them
Europe PMC would have scored 0/8 and read as worthless, when it is in fact strong on an
axis the original six never probed. The corollary is a warning: a benchmark that had
stayed clinical-only would have mis-ranked a connector badly.

**Europe PMC misses Q1–Q5 entirely.** It remains biomedical/PubMed-descended and does
**not** close the modality, book-canon, or historical gap this effort exists to close.

## 6. `n_results` is NOT a comparable column — deliberately omitted

| Connector | min | max |
|---|---:|---:|
| OpenAlex | 7 | 53,884 |
| Crossref | 469,967 | 11,218,320 |
| Europe PMC | 0 | 8,586 |
| PsyArXiv/OSF | 0 | 0 |

Three orders of magnitude apart, because the APIs mean different things by a count.
Crossref's `query=` is a loose OR match across the whole ~160M-record registry;
OpenAlex's `search=` is full-text over an indexed corpus; Europe PMC's is a scoped
biomedical index.

Placed side by side, a reader would infer Crossref has ~900× OpenAlex's coverage. It does
not. **No ranking, tally, or aggregate in this document uses `n_results`.** It is retained
per-connector in `probe/results/*.json` as a within-connector signal only.

## 7. Metadata completeness — the table Task 9 consumes

Count of cells in which each connector actually returned the field.
**Availability, not merely documentation** — a key is listed only where a payload carried it.

| Registry key | Semantic Scholar | OpenAlex | Crossref | Europe PMC | PsyArXiv/OSF |
|---|---|---|---|---|---|
| `doi` | 9/12 | 11/12 | **12/12** | 8/12 | — |
| `pmid` | 4/12 | 7/12 | — | 6/12 | — |
| `pmcid` | 2/12 | — | — | **7/12** | — |
| `openalex_id` | — | **12/12** | — | — | — |
| `semantic_scholar_id` | **12/12** | — | — | — | — |
| `issn` | 7/12 | 11/12 | 3/12 | — | — |
| `isbn` | — | — | **6/12** | — | — |
| `osf_id` | — | — | — | — | — |
| `arxiv_id` | — | — | — | — | — |

| Envelope field | Semantic Scholar | OpenAlex | Crossref | Europe PMC | PsyArXiv/OSF |
|---|---|---|---|---|---|
| `type` | 8/12 | **12/12** | **12/12** | 10/12 | — |
| `venue` | 8/12 | **12/12** | 10/12 | 10/12 | — |
| `publisher` | — | **12/12** | **12/12** | 2/12 | — |
| `oa_status` | 6/12 | **12/12** | — | 7/12 | — |
| `retraction_status` | — | **12/12** | — | — | — |

### What this table establishes

**Only OpenAlex supplies `retraction_status` as a standing field** (explicit boolean on
every record). Crossref *exposes* retraction via `update-to[]` at zero marginal cost —
but only on works that **are** retracted, and none appeared in this sample. These are
different semantics: OpenAlex answers "is this retracted?" always; Crossref answers it
only in the affirmative case. A design that needs "confirmed not retracted" is served by
OpenAlex; one that needs "flag retractions" is served by either.

**`isbn` comes only from Crossref** — consistent with it being the only connector
reaching book canon.

**`osf_id` and `arxiv_id` were never returned by anyone**, including OSF itself (all its
cells were zero-result). Two of the nine registry keys are **unexercised** by this
benchmark; their availability is unestablished, not absent.

**No single connector supplies everything.** Crossref lacks `oa_status` and standing
retraction; OpenAlex lacks `isbn`; Europe PMC is the richest source of `pmcid`.

**Semantic Scholar, now measured across 12 cells, confirms both fixture findings and
contradicts a third.** Confirmed: `publisher` **0/12** and `retraction_status` **0/12** —
it supplies neither, ever. Contradicted: the fixture suggested ~40% of records carry a
registered type with **no** DOI; across 12 top results that pattern occurred **0 times**.
The real distribution is 8 with both, **1 with a DOI but no type**, and **3 with neither**.
So the "type without DOI" case is not the dominant shape — *records with no DOI at all*
are (3/12, 25%), and `semantic_scholar_id` is the only identifier present on every record.

## 8. Venue-class distribution

| Connector | classes produced |
|---|---|
| **Crossref** | `book-chapter` (6), `peer-reviewed-article` (3), `book` (1), `preprint` (1), `grey` (1) |
| **OpenAlex** | `peer-reviewed-article` (10), `unverified` (1), `grey` (1) |
| **Europe PMC** | `peer-reviewed-article` (6), `unverified` (4), `preprint` (2) |
| **PsyArXiv/OSF** | `unverified` (12) |
| **Semantic Scholar** | `peer-reviewed-article` (1) |

**Crossref is the only connector producing real class diversity** — the only source of
`book` and `book-chapter`, and the only one whose distribution reflects that scholarly
literature is not uniformly journal articles. OpenAlex classifies almost everything
`peer-reviewed-article`.

Per its own dossier §3, Crossref resolves **5 of 9** venue classes from registered `type`
alone and **cannot** resolve `guideline`, `institute-publication`, or `commentary` — its
controlled vocabulary has no type for any of them.

## 9. Gaps no connector fills

1. ~~**AEDP / transformance (Q3)** — no hit anywhere.~~ **CLOSED by the keyed Semantic
   Scholar re-run**, which returned Fosha's own *AEDP: Transformance In Action* (2011).
   No other connector reaches it. Note the record carries **neither a DOI nor a registered
   type** — only a CorpusId — so the hit arrives as `venue_class: unverified`,
   `classification_basis: none`. The connector that alone finds AEDP theory cannot say
   what kind of thing it found.
2. **`guideline`, `institute-publication`, `commentary`** — not resolvable from any
   connector's registered `type`. Needs a Layer-4 publisher heuristic.
3. **Modality-institute publications generally** — implied by (2); the AASECT / ICEEFT /
   AEDP / SE / EMDRIA / IFS / Gottman / PACT tier in `source-tiers.yaml` has no connector
   route.
4. **APA PsycNET / PsycINFO** — never probed; deferred candidate. `source-tiers.yaml`
   assigns `apa.org: 1`, and no probed connector reaches that content.
5. **Standing retraction status outside OpenAlex** — see §7.
6. **`osf_id`, `arxiv_id`** — unexercised, availability unestablished.

## Corrections

**OpenAlex tally.** The connector's own report stated *"2 hit / 6 partial / 2 miss"*. Its
recorded cells are **2 hit / 5 partial / 3 miss** — the report miscounted its own table.
The controller repeated the erroneous figure in an interim status summary before
recounting from the files. **All figures in this document are counted from
`probe/results/*.json`.**

**Controller note 9 (`publisher` availability).** Originally claimed publisher might be
Crossref-only, extrapolated from the S2 fixture before aggregation. The aggregate shows
OpenAlex supplies it 12/12. Corrected in place in `probe/CONTROLLER-NOTES.md`, with the
error retained as an example of generalising from one connector without checking the
others.

## Provenance

- 49 cell records, all passing `probe/schema.py::validate`
- Benchmark frozen before any API contact; queries unchanged since
- Each connector's raw C1 payload preserved in `probe/fixtures/`
- Semantic Scholar's attempt history in `probe/results/semantic-scholar-fetch-log.json`
- Cross-connector findings in `probe/CONTROLLER-NOTES.md` (12 entries)
