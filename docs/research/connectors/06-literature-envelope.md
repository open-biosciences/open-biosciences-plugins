# 06 — The literature envelope

**Layer 2 response contract for `psychology-mcp`.**
Governed by ADR-001 §4 (Agentic Biolink schema), §7 (token budgeting), §8 (normative
envelopes), §9 (protocol vs domain types).

Written **after** the five dossiers and the coverage matrix, from measured connector
behaviour rather than from documentation. Where a rule exists to solve a problem the
probe actually found, the finding is cited.

---

## 1. Why this belongs at Layer 2

ADR-001 §4 mandates that every entity response carry a `cross_references` object
conforming to a Key Registry, and §8 fixes the pagination and error envelopes. The
biomedical instance of that mandate is *Agentic Biolink*. Literature needs its own
instance.

The alternative — classifying literature at Layer 4 — is what `psychology-research`
does today, and the probe shows why it fails. `references/source-tiers.yaml` maps
`domain → integer`, so it can only reason about **where a URL points**, never about
**what the item is**. It has 31 entries; one real run cited 25 domains it had never
heard of.

The four measured connectors return `type` on 10–12 of 12 cells and `publisher` on up
to 12 of 12. The metadata exists. It is simply thrown away before the consumer sees it.
**Normalising it is the server's job**, and doing so is what lets the domain map retire
to its true role as a web-results fallback.

## 2. Two axes

**Axis A — venue class.** *What the item is.* Nine values (§3). Resolved server-side.

**Axis B — discovery route.** *Which connector surfaced it.* Recorded for provenance and
for ADR-001 §6 triangulation. **Never contributes to venue class or to any tier.**

An index is a lookup vehicle, not a peer-review warrant. Tiering `api.openalex.org`
would classify a consumer-media blog post as peer-reviewed on the grounds that OpenAlex
indexed it. The probe makes the point concrete: OpenAlex's Q4 top result was the phrase
*"Heroine's Journey"* used as a STEM-education metaphor, and its Q8 top result was
ecosystem-services literature. Both are well-formed `peer-reviewed-article` records. The
index's involvement says nothing about either.

## 3. Venue classes

`peer-reviewed-article` · `book` · `book-chapter` · `institute-publication` ·
`preprint` · `guideline` · `grey` · `commentary` · `unverified`

### 3.1 Four vocabularies, one target

No two connectors describe type the same way. The server owns this normalisation; the
consumer must never see raw connector vocabulary.

| Venue class | Crossref `type` | OpenAlex `type` | Europe PMC | Semantic Scholar `publicationTypes` |
|---|---|---|---|---|
| `peer-reviewed-article` | `journal-article` | `article` | `source: MED`/`PMC` + journal | `JournalArticle`, `ClinicalTrial`, `Review` |
| `book` | `book`, `monograph`, `edited-book` | `book` | `source: NBK` | — |
| `book-chapter` | `book-chapter`, `reference-entry`※ | `book-chapter` | — | — |
| `preprint` | `posted-content` | `preprint` | `source: PPR` | — |
| `guideline` | *(no type)* | *(no type)* | *(no type)* | *(no type)* |
| `institute-publication` | *(no type)* | *(no type)* | *(no type)* | *(no type)* |
| `commentary` | *(no type)* | *(no type)* | *(no type)* | *(no type)* |
| `grey` | `report`, `dissertation`, `dataset`※ | `dissertation`, `report` | — | — |
| `unverified` | *(fallback)* | *(fallback)* | *(fallback)* | *(fallback)* |

※ **Judgement calls inherited from `03-crossref.md` §3.1, not direct mappings.**
`reference-entry` → `book-chapter` (an encyclopedia entry has a `container-title` and
functions as a chapter). `dataset` → `grey` is **low confidence**: the probe's one
`dataset` record was an APA PsycTherapy streaming-video catalogue entry, which could
equally be argued `unverified`. Both are recorded as interpretations, not rules.

Only 6 of Crossref's registered-type vocabulary appeared across 17 examined items;
`monograph`, `edited-book`, `report`, `dissertation`, `proceedings-article`, `standard`
are mapped above **from the vocabulary, not from observation.**

### 3.2 Three classes no connector can resolve

**`guideline`, `institute-publication`, `commentary` have no source type in any
vocabulary.** Crossref's controlled vocabulary has no entry for any of them; nor do the
other three. They would register indistinguishably as `journal-article`, `report`, or
`other`.

This is a measured dead end, not an oversight. `institute-publication` is the hardest:
it is defined by **who published** the item, not what type it is — and it is precisely
the class that `source-tiers.yaml`'s AASECT / ICEEFT / AEDP / SE / EMDRIA / IFS /
Gottman / PACT tier depends on.

**The envelope does not resolve these three.** It returns `unverified` with the
publisher string intact, and a Layer-4 publisher heuristic decides. Pretending
otherwise would be the server asserting a classification it cannot make.

## 4. Resolution order

The probe found two cases the naive order gets wrong. Both are handled here.

```
1. provenance override   record is repository- or preprint-sourced
                         → venue_class = preprint, basis = provenance
2. registered metadata   DOI resolves with a registered type
                         → classify from that type, basis = registered
3. index-asserted type   no DOI, but the connector returned a type
                         → classify from that type, basis = index-asserted
4. neither               → venue_class = unverified, basis = none
```

### 4.1 Why step 1 exists — the preprint-DOI inversion

A published PsyArXiv preprint's `attributes.doi` holds the **published journal
article's** DOI, not an OSF-minted preprint DOI. Crossref therefore types it
`journal-article`. Two of five records checked carry a `relation.has-preprint`
back-reference proving the records are distinct
(`05-psyarxiv-osf.md` §3).

A DOI-first order would classify a preprint record as `peer-reviewed-article` — an
error in the direction that matters most, since it launders a preprint into peer-reviewed
standing.

**Provenance beats DOI resolution.** A record surfaced by a repository connector, or
carrying a preprint source marker (Europe PMC `source: PPR`, Crossref `posted-content`),
is a preprint regardless of what its DOI resolves to. Where a `relation.has-preprint`
link exists, both identifiers are carried (§5).

*Corroboration limit:* the controller independently confirmed that many OSF records
carry no DOI at all (5/5 sampled), but did not re-verify the populated-DOI case. The
rule is defensive and cheap either way.

### 4.2 Why step 3 exists — type without a DOI

Spec §6.2 as drafted flattened *no DOI* to `unverified`, discarding a type the API had
already supplied. The probe shows this is a **recurring class, not an edge case**:

| Connector | records with a type but no DOI |
|---|---|
| Europe PMC | Q2 (`pubType: review-article`, `source: PMC`), C2 — ~11% of sampled results |
| Semantic Scholar | 2 of 5 C1 records (`publicationTypes: ['Review']`, only `CorpusId`) — 40% of that sample |

Flattening these loses real information and mis-sizes the tierable corpus.

**`classification_basis` is the fix.** Rather than one bucket meaning both *"we don't
know"* and *"we know but not authoritatively"*, the envelope carries the class **and**
how it was established:

| `classification_basis` | Meaning |
|---|---|
| `provenance` | Established by the record's source, not its identifier (§4.1) |
| `registered` | From a DOI-resolved registered type — a registration authority's assertion |
| `index-asserted` | From the connector's own type field, no DOI — the index's assertion |
| `none` | No basis; `venue_class` is `unverified` |

This keeps the trust distinction the DOI-first rule was protecting, without destroying
the data. **The consumer decides whether `index-asserted` is good enough for a given
claim** — which is editorial policy, and belongs at Layer 4 (§9).

## 5. Literature Key Registry

The bibliographic analogue of ADR-001 Appendix A. Every work response carries
`cross_references` with whichever keys resolve.

| Key | Measured availability (cells returning it) |
|---|---|
| `doi` | Crossref 12/12 · OpenAlex 11/12 · Europe PMC 8/12 · S2 1/1 |
| `pmid` | OpenAlex 7/12 · Europe PMC 6/12 · S2 1/1 |
| `pmcid` | **Europe PMC only** 7/12 |
| `openalex_id` | **OpenAlex only** 12/12 |
| `semantic_scholar_id` | **S2 only** 1/1 |
| `issn` | OpenAlex 11/12 · Crossref 3/12 · S2 1/1 |
| `isbn` | **Crossref only** 6/12 |
| `arxiv_id` | **never observed** — availability unestablished |
| `osf_id` | **never observed** — availability unestablished |

Null-handling and cardinality follow ADR-001 Appendix A. `arxiv_id` and `osf_id` remain
in the registry: they were unexercised by this benchmark (OSF returned no results at
all), which is not evidence of absence.

**No connector supplies the whole registry.** Crossref is the sole source of `isbn`;
Europe PMC the sole source of `pmcid`. Two connectors agreeing on a DOI is a
triangulation success under ADR-001 §6; single-source provenance is a recorded weakness,
carried in Axis B.

## 6. Retraction status

The probe found **two different semantics**, and the envelope must not conflate them.

| Connector | Behaviour |
|---|---|
| **OpenAlex** | `is_retracted`, an explicit boolean, present on **12/12** cells |
| **Crossref** | `update-to[]` with `type: "retraction"`, present **only on works that are retracted** — verified live against a real retracted work; zero marginal request cost |
| Europe PMC, S2 | Never exposed |

OpenAlex answers *"is this retracted?"* always. Crossref answers it **only in the
affirmative**. An absent Crossref `update-to` is not a negative — it is silence.

Envelope field:

| `retraction_status` | Meaning |
|---|---|
| `retracted` | An affirmative retraction signal was found |
| `not-retracted` | A source that always reports the field said no — currently OpenAlex only |
| `unknown` | No source consulted reports the field. **Not a synonym for not-retracted.** |

**A record whose only source is Crossref, Europe PMC, or S2 is `unknown`, never
`not-retracted`.** Answering spec §10's open question 3: a standing retraction check
costs **zero extra calls if OpenAlex is in the route**, and is **not available at any
price** from Europe PMC or S2 alone.

## 6a. Source precedence — whose assertion wins

§5 records **which connector returns a field**. It does not say **whose answer wins when
two disagree**, and ADR-001 §6 mandates triangulation across `cross_references` without
specifying conflict resolution. That gap is closed here.

The frame is adopted from [AGE-539], already accepted in this workspace:

> **Authority selects the source. Volatility decides whether to re-verify it live.**

Its two non-obvious consequences transfer intact:

- **A lower tier can outrank a higher one within its own scope.** OpenAlex is not
  authoritative for what Crossref registered, but it *is* authoritative for its own
  `is_retracted` determination, which Crossref does not make.
- **Conflicts resolve by scope first, then tier, then recency.** Most apparent conflicts
  are scope mismatches, not contradictions.

### 6a.1 Authority by field

The biomedical analogue is `prior-art-api-patterns.md` §4.5, where Bioregistry and
identifiers.org are the *authoritative registries* for identifier prefixes. **The
literature equivalent is Crossref and DataCite as DOI registration agencies** — which is
exactly why `classification_basis: registered` outranks `index-asserted`.

| Field | Authority | Rationale |
|---|---|---|
| `type`, `publisher`, `venue`, `isbn`, `issn` | **Crossref** (registration agency) | The registrant declared it. Every index is repeating that declaration, sometimes lossily — OpenAlex reduced Crossref's six observed types to `article` in our sample |
| `doi` | **Crossref**, normalised to bare form | Registration agency of record |
| `retraction_status` | **OpenAlex** for a standing determination; **Crossref** for an affirmative notice | Scope split, not a tier conflict. Only OpenAlex answers "is this retracted?" always (§6) |
| `pmid`, `pmcid` | **Europe PMC** | Sole source of `pmcid`; NLM-descended |
| `openalex_id` | OpenAlex | Sole issuer |
| `semantic_scholar_id` | Semantic Scholar | Sole issuer. **Its distinctive value is a stable id for records with no DOI** — 40% of its own observed sample |
| `oa_status` | **OpenAlex** | Richest OA modelling; note Semantic Scholar's `openAccessPdf` is non-null even when `status: CLOSED` |
| `venue_class` | **Derived, never fetched** | Computed from `type` + publisher per §3–§4. No connector supplies it |

**Where an index disagrees with the registration agency, the registration agency wins and
the disagreement is recorded** — `conflict: true` with both citations, per AGE-539. A
documented disagreement is more useful than a confident wrong pick.

**Unresolvable-by-anyone stays unresolvable.** No precedence rule rescues `guideline`,
`institute-publication` or `commentary` (§3.2); precedence orders sources that *have* an
answer.

## 6b. Volatility and caching

Bibliographic metadata is unusually cacheable — but **not uniformly**, and the exception
is the field that matters most.

| Volatility | Fields | Policy |
|---|---|---|
| **low** | `doi`, `title`, `authors`, `year`, `type`, `venue`, `publisher`, `isbn`, `issn`, all registry ids | Cache indefinitely. A published work's registration does not change |
| **derived-low** | `venue_class`, `classification_basis` | Cache with the inputs. Recompute only if an input changes or §3–§4 changes |
| **high** | **`retraction_status`**, `oa_status` | **Never cache.** Re-verify on read |

**The asymmetry is the whole point.** A work becomes retracted *after* you cached it —
that is the event the field exists to report. Caching `retraction_status` freezes the one
signal that must stay live, on the one connector that supplies it as a standing
determination. `oa_status` is milder but moves the same direction: embargoes lapse,
publishers flip licences.

**Practical shape:** cache the classification, re-verify the retraction. That is also
where the cost actually is — `venue_class` is expensive to compute (it may need a DOI
resolution) and stable once computed, while a retraction check is one field on a request
already being made.

**This is the sanctioned route around Semantic Scholar's rate limit.** Its distinctive
contributions — the identifier crosswalk and CorpusIds for DOI-less records — are all
`low` volatility, so they cache indefinitely. A throttled connector is far less
constraining for permanent facts than for volatile ones. It does **not** rescue coverage:
you cannot cache a search you were never able to run.

### 6b.1 Batching is not currently a lever

MEASURED across the five dossiers — batching is weak or absent, and every "maybe" is
unverified:

| Connector | Batch support |
|---|---|
| Semantic Scholar | `/paper/batch` POST **documented, not verified** (429 throughout) |
| Crossref | **No true multi-DOI batch** in the public `/works` route |
| OpenAlex | No batch exercised; a `filter=` OR-join is plausible, **unverified** |
| Europe PMC | **None observed** — N works means N calls |
| PsyArXiv/OSF | Not confirmed |

Do not design a gateway assuming batch amortisation. A targeted verification pass against
the three keyless connectors would settle it cheaply; until then, **caching is the only
demonstrated lever** and the per-connector rate discipline in the constitution's Required
Patterns is what keeps N-call fan-out survivable.

## 7. Slim mode (ADR-001 §7)

ADR-001 §7 mandates `slim=True` on batch tools and specifies `id`/`name`/`score` for
biomedical entities. Literature needs its own triple — **an adaptation, not an
inheritance**.

**Slim projection: `doi`, `title`, `venue_class`.**

Chosen so an agent can triage **relevance and admissibility together**. ADR-001's
`score` alone cannot distinguish a peer-reviewed article from a blog post, and the
probe shows why that matters: a connector can return a perfectly well-formed record
that is the wrong *kind* of thing entirely.

Default page size 50 (ADR-001 §5). `classification_basis` is **not** in the slim
projection — a consumer applying a basis policy needs the full record.

Native support is uneven and belongs in the wrapping cost estimate: S2's `fields` and
OpenAlex's `select` are true server-side projections; Crossref's `select` is partial;
Europe PMC's `resultType=lite` is documented but unverified.

## 8. Canonical envelopes (ADR-001 §8)

Adopted **verbatim** — these are protocol, not domain, and must not be re-specified.

```json
{
  "items": [ ... ],
  "pagination": { "cursor": "opaque_string", "total_count": 1540, "page_size": 50 }
}
```

```json
{
  "success": false,
  "error": {
    "code": "UNRESOLVED_ENTITY",
    "message": "The input 'Heroine's Journey' is not a resolved CURIE.",
    "recovery_hint": "Call 'search_works' to get a valid DOI first.",
    "invalid_input": "Heroine's Journey"
  }
}
```

Per ADR-001 §3, `get_work` accepts **only** a resolved identifier; a raw string returns
`UNRESOLVED_ENTITY`. The DOI is the CURIE. Semantic Scholar additionally accepts
`CorpusId:`, `PMID:`, `ARXIV:` and `MAG:` prefixes — useful precisely for the §4.2
records that have a type but no DOI.

**`total_count` carries a caveat.** §6 of the coverage matrix establishes that connector
result counts are not comparable — three orders of magnitude apart, because Crossref's
`query=` is a loose OR over ~160M records while OpenAlex's is full-text over an indexed
corpus. `total_count` is a **within-connector** signal. A gateway must never sum or
compare it across connectors, and must never rank on it.

## 9. Protocol vs domain types (ADR-001 §9)

- **Protocol types** — `CrossReferences`, `PaginationEnvelope`, `ErrorEnvelope`. Importable
  by any model; **must not** import a domain type.
- **Domain types** — `Work`, `Venue`. May import protocol types.

`venue_class` and `classification_basis` are **enumerations on the domain type `Work`**,
not protocol types. They describe a literature item, not the transport.

## 10. What stays at Layer 4

**The server reports what a thing *is*. The consumer decides what it is *worth*.**

Out of scope for this envelope, and deliberately so:

- **Paradigm overrides.** *"For RSD, tier-5 grey literature is the canonical evidence
  base"* is `psychology-research`'s editorial judgement, expressed in
  `references/modality-canon.md`. It is not a property of the work.
- **Tier numbers.** The envelope emits no integer tier. `source-tiers.yaml` is a
  consumer policy artefact.
- **Basis policy.** Whether `index-asserted` suffices for a `VERIFIED` label is the
  consumer's call (§4.2).
- **The domain-map fallback.** Web results with no metadata still need
  `source-tiers.yaml`. The envelope does not replace it; it makes it the fallback it
  always really was.
- **The three unresolvable classes** (§3.2) — publisher-string heuristics live here.

This split is what makes the envelope reusable by a consumer with different editorial
policy — including `bio-research`, whose adoption is deferred to AGE-554.

## 11. Open items

1. **`dataset` → `grey`** is low-confidence (§3.1), resting on one manually-verified record.
2. **`arxiv_id`, `osf_id`** unexercised (§5).
3. **Europe PMC `resultType=lite`** unverified as a slim mechanism (§7).
4. **Preprint-DOI inversion** corroborated only in part (§4.1).
5. **Semantic Scholar contributed one cell.** Its `fields` projection and identifier
   crosswalk are documented from a single fixture, not a completed run.
6. **Q3 (AEDP transformance) had no hit from any connector.** No envelope design fixes a
   retrieval gap; recorded here so §3.2's institute-publication problem is not mistaken
   for the whole of it.
7. **Batch support is unverified for three connectors** (§6b.1). A cheap verification pass
   against the keyless three would either enable batch amortisation or close the question.
8. **Cache invalidation on registration change is unspecified.** §6b treats registered
   metadata as immutable, which is true in practice but not absolutely — a registrant can
   update a Crossref record. Crossref's `indexed.date-time` is a candidate freshness key;
   not designed here.
