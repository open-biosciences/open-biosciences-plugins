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

## 5. Crossref rate limit was initially exceeded

The Crossref agent found, from live `x-rate-limit-*` response headers, that the
adapter's initial `RATE = 0.2` (5 req/s) was above Crossref's declared 3 req/s cap,
and tightened it to `0.35` after the run. No 429s were observed, but the recorded
cells were fetched slightly over-rate.

Not a data-integrity problem — the responses are genuine and the counts stand. Worth
noting in `DECISION.md` §7.1 as an argument for reading `x-rate-limit-*` headers at
runtime rather than hardcoding a rate, which is already in that dossier's §8 residual
risks.
