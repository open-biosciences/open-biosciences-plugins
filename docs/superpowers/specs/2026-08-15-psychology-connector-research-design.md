# Psychology-research connector selection and source-tier redesign

**Date:** 2026-08-15
**Status:** Draft — awaiting maintainer review
**Repo:** `open-biosciences-plugins`
**Deliverable location:** `docs/research/connectors/`

**Tickets:** unblocks [AGE-552]; answers question 3 of [AGE-548]; consumer-side context in [AGE-542], [AGE-559], [AGE-560]; named follow-on to [AGE-554].

---

## 1. Problem

`psychology-research` ships `.mcp.json` as `{"mcpServers": {}}` — unchanged across versions 0.1.0, 0.2.0, and 0.2.1 — and `skills/psychology-evidence-builder/SKILL.md` declares `bindings: literature: []`. The plugin therefore has no literature connector. Literature retrieval falls through to `~~web` and is tier-capped below `VERIFIED`.

This is documented as deliberate (`CONNECTORS.md`: *"Tier-1a ships with `mcpServers: {}`"*), and the skills degrade honestly. The defect is not dishonesty; it is that the Tier-2 population step has never been executed, and that an empty `mcpServers` object reads as *"configured with zero servers"* rather than *"no connector layer."*

The cost is now measured rather than hypothesised. On 2026-08-14 a consumer run bound a PubMed MCP server in-session and executed the evidence-builder procedure. Six research questions returned `UNRESOLVED`, and the run's own diagnosis was explicit:

> These six are a **binding limitation, not an absence of literature.** … for modality theory, qualitative practice literature, or book-form canon, prefer Semantic Scholar or state the paradigm fit. No Semantic Scholar connector is bound in this session, and PubMed's own scope note excludes non-medical psychology.

A second, independent problem compounds it. `references/source-tiers.yaml` is a flat `domain → integer` map of 31 entries. `source_tiers_loader.lookup_tier()` returns `None` on a miss and `validators/source_tier_minimum.py` **skips any source it cannot tier**. A single real run cited 25 domains absent from the map. Adding index-type connectors to that model makes it worse, not better: `api.openalex.org: 1` would tier a consumer-media blog post as peer-reviewed on the grounds that OpenAlex indexed it.

These are one problem. The domain map exists **because web-search results carry no metadata**. Connectors are what supply metadata. Selecting connectors and fixing the tier model are therefore a single change, sequenced.

## 2. Architectural framing: skills vs. connectors

`psychology-research` is a **general-purpose domain pack** — the behavioural, cognitive, clinical, and social-science counterpart to `bio-research`. It is not a relationship-assessment tool.

| Layer | Nature | Examples | Responsibility |
|---|---|---|---|
| **Skills** | Specialised consumers | `relational-vibrancy`, future psychometric / cognitive / organisational workflows | Methodology, rubrics, multi-lens synthesis, application-specific output |
| **Connectors** | General substrate | OpenAlex, Semantic Scholar, Crossref, Europe PMC, PsyArXiv/OSF, PubMed | Literature search, DOI resolution, venue classification, citation metadata, retraction verification |

Two consequences bind this specification:

1. **Connectors are unaware of skills.** A connector is designed, evaluated, and tiered purely as a general scholarly data source. It does not know whether it is serving a relational assessment, a scale-validation review, or a cognitive-neuroscience agent.
2. **`relational-vibrancy` is a consumer, not the boundary.** It supplied the stress test and the initial gap list. It does not define the requirement. The design must not over-fit to vibrancy terminology, dyadic attachment, or canon-specific structures.

The benchmark suite in §4 is written to this standard: it is a general psychology benchmark that happens to have been seeded by a vibrancy run, not a set of vibrancy queries.

## 3. Scope

### In scope

- Five connector dossiers: **Semantic Scholar, OpenAlex, Crossref, Europe PMC, PsyArXiv/OSF**.
- A live coverage probe of all five against a **pre-registered 12-query benchmark** (§4).
- A redesign of the source-tiering model (§6), **specified as domain-agnostic science infrastructure, with implementation targeted at `psychology-research`**.
- One decision document (§7) that answers AGE-548 question 3 and specifies concrete file deltas.

### Out of scope

- Writing any MCP server. Each dossier makes a bind / wrap / drop recommendation; acting on a "wrap" recommendation is separate work.
- **Implementing** the tier model. This effort specifies it and names its implementation target; the code change lands in the follow-on PR alongside the connector deltas.
- Changes to `psychology-research` skills, commands, or validators.
- Changes to `bio-research`. Its adoption of the tier model is a named follow-on under AGE-554.
- Changes to `hci-canon`. The contradictions found there (§7.3) are recorded as findings, not fixed here.
- Applying the deltas. `DECISION.md` proposes; a separate PR against AGE-552 applies.

### Deliverables

All under `docs/research/connectors/`:

| File | Contents |
|---|---|
| `README.md` | Method, the frozen benchmark, cell-record schema, how to re-run |
| `00-coverage-matrix.md` | 5 APIs × 12 queries = 60 cells, with example records |
| `01-semantic-scholar.md` | Dossier (§5 template) |
| `02-openalex.md` | Dossier |
| `03-crossref.md` | Dossier |
| `04-europe-pmc.md` | Dossier |
| `05-psyarxiv-osf.md` | Dossier |
| `06-tier-model.md` | The two-axis tiering redesign (§6) |
| `DECISION.md` | Binding decision, AGE-548 q3 answer, proposed deltas, limitations (§7) |

### Candidate selection rationale

| Candidate | Why included |
|---|---|
| **Semantic Scholar** | The plugin's own declared Tier-2 binding, named in `CONNECTORS.md`, `SKILL.md` (twice), and `modality-canon.md`. Broad disciplinary coverage. |
| **OpenAlex** | Broadest open scholarly index; covers humanities, books, and non-biomedical psychology. Keyless. |
| **Crossref** | DOI registry including monographs and book chapters. Supplies the item metadata the tier model needs, and exposes retraction/update notices. |
| **Europe PMC** | Candidate **replacement** for the PubMed connector rather than an addition — superset scope (preprints, NCBI Bookshelf) and a richer API. Whether it supersedes PubMed is a research finding, not an assumption. |
| **PsyArXiv / OSF Preprints** | The psychology preprint server. Occupies the slot bioRxiv was wrongly proposed for; bioRxiv is molecular and cell biology and returns near-nothing for this domain. |

**Considered and deferred, with reasons recorded so they are not re-litigated:**

- **APA PsycNET / PsycINFO** — the canonical psychology index and the correct answer on paper. Believed licensed with no open API. Not included as a dossier; `DECISION.md` §5 must state the consequence if this holds, because `source-tiers.yaml` currently assigns `apa.org: 1`.
- **ERIC** — education, counselling, and school psychology. Relevant under the general-purpose framing; deferred to a second pass.
- **medRxiv, Unpaywall, DOAJ, CORE, Internet Archive / Open Library** — plausible, but each addresses a narrower slice than the five selected. Internet Archive specifically is the known route to historical primary sources (Q5) and should be revisited if no selected connector resolves that query.
- **bioRxiv** — explicitly rejected. Wrong domain.

## 4. The benchmark suite

Twelve queries: ten measuring coverage, two controls. Frozen before any API is contacted.

**Pre-registration matters and is the point.** The coverage matrix is intended to be citable evidence. Queries chosen after seeing what an API returns are not evidence, they are shopping. Q1–Q8 derive from a gap list recorded on 2026-08-14, before any connector was under consideration; Q9–Q10 were added to close a subject-axis blind spot identified during design, also before any API contact. This provenance is recorded in `README.md`.

Queries span two independent axes. **Format** — does the connector index this *kind* of artefact. **Subject** — does the connector reach this *discipline's* publisher ecosystem. A benchmark strong on one axis and blind on the other selects connectors that look uniformly excellent and then underperform.

| # | Query | Format axis | Subject axis |
|---|---|---|---|
| Q1 | IFS — parts, Self-led vs. protective | Contemporary clinical | Clinical / psychotherapy |
| Q2 | Somatic Experiencing / Sensorimotor — window of tolerance | Contemporary clinical | Somatic / trauma |
| Q3 | AEDP transformance | Contemporary clinical | Experiential psychotherapy |
| Q4 | Heroine's Journey (Murdock / Frankel) | **Monograph / book canon** | Narrative psychology |
| Q5 | Marston DISC, 1928 — situational vs. fixed-trait | **Historical primary** | Personality / historical |
| Q6 | Secure base / safe haven in *established* adult romantic dyads | Empirical journal | Attachment / relational |
| Q7 | Basson 2000 — responsive vs. spontaneous sexual desire | Empirical journal | Sexology |
| Q8 | Shared novel activity and aesthetic engagement as relational maintenance | Empirical journal | Social / self-expansion |
| Q9 | Measurement invariance testing in psychological scale validation | Empirical journal | **Quantitative / psychometrics** |
| Q10 | Working memory capacity and fluid intelligence | Empirical journal | **Experimental / cognitive** |
| **C1** | EFT as an evidence-based couple therapy (Wiebe & Johnson 2016) | *Positive control* | *Harness check* |
| **C2** | Neuro-Dynamic Co-Regulation Index (Vanderbilt & Hayes 2019) | *Negative control* | *Hallucination check* |

**Q6 note.** PubMed returned only *fledgling*-relationship literature for this question. The query is deliberately scoped to established dyads to preserve that discrimination.

**C1 is scored separately from the coverage cells.** It validates the harness — an API that misses it has a broken client, not a coverage gap. It is not counted toward any connector's coverage score.

**C2 is a fabricated construct with a fabricated citation.** The passing result is an explicit **zero hits or empty response**. Any non-empty, confident-looking result is a recorded finding against that connector or its wrapper. This control exists because fabricated citations have already reached a user-facing surface in this ecosystem (AGE-547); a connector that fuzzy-matches a plausible non-existent construct will reproduce that failure.

### Cell record schema

Each of the 60 cells records:

| Field | Values |
|---|---|
| `result` | `hit` / `partial` / `miss` |
| `n_results` | integer |
| `top_result` | title, authors, year |
| `venue_class` | `journal-article` / `book` / `book-chapter` / `preprint` / `institute-publication` / `grey` / `unknown` |
| `doi_present` | boolean |
| `metadata_completeness` | which of {DOI, type, venue, publisher, retraction status, OA status} were returned |
| `notes` | free text |

`metadata_completeness` is the field that feeds §6. A connector that returns results but no venue type cannot support item-level tiering, which is a first-order selection criterion independent of coverage.

## 5. Dossier template

Each `0N-<api>.md` uses this fixed structure so the five are comparable in the decision matrix.

| § | Content |
|---|---|
| 1 | **Identity and access** — base URL, auth model, key requirement, published and observed rate limits, ToS and attribution obligations. *(Non-trivial: the PubMed connector already imposes a DOI-link attribution requirement. Assume each has its own until verified.)* |
| 2 | **Mechanics** — request and response format, pagination model, filtering, batch support, error behaviour |
| 3 | **Item metadata** — what the API returns *per record*: DOI, type, venue, publisher, retraction status, OA status, identifiers. **This section is the input to §6.** |
| 4 | **Measured coverage** — this API's 12 cells, with example records |
| 5 | **Existing MCP server** — does one exist; keyless or credentialed; maintainer; currently live |
| 6 | **Tier implications** — which venue classes this connector can and cannot resolve |
| 7 | **Recommendation** — bind existing / wrap ourselves / drop, with reasoning and residual risk |

Section 3 is what distinguishes this from an API survey. A connector's value here is not only what it finds but whether it returns enough metadata to tier what it finds.

## 6. Source-tier model redesign

### 6.1 Current model and its failure modes

`source-tiers.yaml` maps `domain → integer` across 31 entries. `lookup_tier()` returns `None` on a miss; `source_tier_minimum` skips untiered sources.

| Failure | Evidence |
|---|---|
| Coverage — untiered domains outnumber tiered ones in real use | 25 untiered domains cited in a single run against 31 in the map |
| Silent skip — an untiered source produces no signal at all | `source_tiers_loader.py:43-44`, `source_tier_minimum.py:74-79` |
| Locator ≠ source — a Tier-6 host resolving a real peer-reviewed item is rejected as Tier-6 | ResearchGate as sole public locator for a genuine journal article |
| Paradigm mismatch — grey literature that *is* the canonical evidence base for a construct is warned against | Consumer-media sources are the primary literature for constructs with no Tier-1 home |
| No preprint concept — an article and its own preprint are indistinguishable | A journal article and its medRxiv preprint both cited, undifferentiated |
| **Index sources are unrepresentable** | An index returns items from thousands of domains; tiering the index tiers everything it touches |

The last row is what makes this a blocker rather than a backlog item: the connectors this specification selects cannot be added to the current model without corrupting it.

### 6.2 Proposed model — two axes

**Axis A — venue class.** *What the item is.* One of: `peer-reviewed-article`, `book`, `book-chapter`, `institute-publication`, `preprint`, `guideline`, `grey`, `commentary`, `unverified`.

**Axis B — discovery route.** *How the item was found.* The connector name. Recorded for provenance and reproducibility. **Never contributes to tier.**

This decoupling is the correction. An API connector is a lookup vehicle, not a peer-review warrant.

### 6.3 Resolution order

1. **Item carries a DOI with registered metadata** → tier from Axis A using the item's own `type`, venue, and publisher. The locator domain is irrelevant. *This is the locator-vs-source fix, structurally rather than by exception list.*
2. **No DOI** → fall back to the existing domain map, which survives in its true role as the web-results fallback.
3. **Neither** → `UNTIERED`, which **must warn**. Never a silent skip. *This is the vacuous-pass fix.*

### 6.4 Consequences that fall out once item metadata is available

- **Retraction check.** Crossref exposes retraction and update notices. A retracted item is rejected regardless of venue class. Low cost; the highest-value integrity check available to research output.
- **Preprint as its own class**, not a downgraded article. Resolves the article-plus-its-own-preprint double count.
- **Paradigm override.** `references/modality-canon.md` already declares per-modality `preferred_databases`. Extend it to per-topic venue-class overrides so *"for topic X, institute publications and grey literature are the canonical evidence base"* is expressible, and `source_tier_minimum` stops warning on the best available evidence for a construct with no peer-reviewed home.

### 6.5 Generality and the shared layer

`06-tier-model.md` is written as **domain-agnostic science infrastructure**. Nothing in Axis A, Axis B, the resolution order, retraction handling, or preprint classification is psychology-specific.

Implementation is **targeted at** `psychology-research`, which owns `source_tiers_loader.py` and the validator suite — and is executed in the follow-on PR, not here (§3). `bio-research` has no `scripts/` directory and therefore no validators; adopting this model there is a **named follow-on under AGE-554**, separate again. This ordering is deliberate: it produces the design a shared-layer extraction needs without making this work depend on an unresolved packaging question, while AGE-548's scope boundary remains open.

The interdisciplinary case is the payoff. A psychoneuroimmunology or psychiatric-genetics query blending `bio-research` (PubMed, NCBI) and `psychology-research` (OpenAlex, Semantic Scholar, Crossref) sources should tier uniformly, with retraction, preprint, and venue-type rules applying identically regardless of which connector surfaced the item.

## 7. The decision document

`DECISION.md` carries five sections.

**7.1 Binding decision.** Which connectors are declared in `psychology-research/.mcp.json`, rolled up from each dossier's §7, with the residual capability gap stated plainly.

**7.2 AGE-548 question 3.** *Does the plugin own MCP server declarations, or does the consumer supply them?* Argued from the in-repo `bio-research` precedent: it declares five keyless public HTTP servers and leaves everything credentialed to the consumer. Adopting that same line — **plugin owns keyless public servers; consumer owns credentialed and per-institution adapters** — resolves the narrow question AGE-552 is blocked on without requiring the full scope ADR.

**7.3 Producer/consumer contradictions found during research.** Recorded, not fixed:

- `hci-canon` `.claude/skills/relational-vibrancy/SKILL.md:70` names `pubmed-database / OpenAlex / Europe PMC` as the literature sources; `psychology-research` names `pubmed, semantic-scholar`. The consumer and the producer disagree about which non-PubMed source is intended.
- The same file's frontmatter enumerates seven dissertation modalities plus an eighth lens, `SKILL.md:86` says *"omit to run all seven"*, and the 2026-08-14 run report says *"four of the eight lenses."*

**7.4 Proposed deltas.** Written out for `.mcp.json`, `CONNECTORS.md`, `source-tiers.yaml`, `source_tiers_loader.py`, and the affected validators. **Proposed, not applied.**

`psychology-research/` is mirrored downstream into the separate `psychology-research-plugins` repository by `rsync --delete` from this upstream. Every delta must therefore be authored **here** and reach the mirror by that sync — never hand-edited in the mirror, which the next sync would silently discard. `DECISION.md` names the sync as an explicit step in the apply-PR sequence.

**7.5 What remains unsatisfiable.** Stated plainly, because the alternative is advertising capability that does not exist. At minimum: if no selected connector reaches APA/PsycINFO-class content, then `source-tiers.yaml` assigning `apa.org: 1` and the marketplace description promising *"source hierarchy, claim provenance"* both describe reach the plugin cannot deliver. Whatever the benchmark shows, the honest ceiling goes here, and any connector whose coverage is partial gets its partiality named rather than averaged away.

## 8. Execution sequence

1. **Freeze.** Write `README.md` with the 12 queries, the cell-record schema, and the provenance note. **Maintainer approves before any API is contacted.** This is the gate that makes the benchmark pre-registered rather than retrospective.
2. **Dossiers, one API at a time**, in order: Semantic Scholar → OpenAlex → Crossref → Europe PMC → PsyArXiv/OSF. Each is complete (§1–§7 of the template, including its 12 probe cells) before the next begins.
3. **Assemble** `00-coverage-matrix.md` from the five dossiers' §4.
4. **Write** `06-tier-model.md`, informed by the aggregated §3 metadata findings.
5. **Write** `DECISION.md`.
6. **Stop.** Applying deltas is a separate PR against AGE-552.

Steps 2 through 5 run inline. No agent fan-out for artefact production.

## 9. Non-goals

- Building MCP servers.
- Reconciling `bio-research` to the new tier model.
- Fixing the `hci-canon` contradictions in §7.3.
- Applying any delta to `.mcp.json`, `CONNECTORS.md`, or `source-tiers.yaml`.
- Re-opening the AGE-548 scope boundary beyond its question 3.
- Any change to `psychology-research`'s crisis-safety surface, evidence-label vocabulary, or `local_context` tier rule. These are settled and reusable as-is.

## 10. Risks and open questions

| Risk | Mitigation |
|---|---|
| A selected connector has no public MCP server, forcing wrap-or-drop | Dossier §5 establishes this per API before any binding decision; "wrap" is a recommendation this effort does not act on |
| Probe results look strong but reflect query phrasing rather than coverage | Two axes per query, a positive control, and a negative control; phrasing is frozen and published |
| The tier redesign grows into a validator rewrite | §3 puts implementation in the follow-on PR and scopes its target to `source_tiers_loader.py` and the tier-consuming validators. A broader validator repair is separate work |
| PsycNET turns out reachable after all, changing the recommendation | Recorded as an open question; a reversal is cheap before deltas are applied and expensive after |
| Q5 (1928 primary source) resolves in none of the five | Expected. Internet Archive / Open Library revisited in a second pass; the honest finding goes in `DECISION.md` §7.5 |
| Rate limits make 60 probe cells slow or throttled | Dossier §1 establishes limits before probing; probes are sequential per API, not parallel |

**Open questions carried into execution:**

1. Does Europe PMC supersede the PubMed connector, or complement it? Answered by `04-europe-pmc.md` §4 and §6.
2. Is APA PsycNET reachable by any programmatic route? A bounded check inside `DECISION.md` §7.5, not a sixth dossier.
3. Does any connector expose retraction status directly, or is Crossref required as a second lookup for every DOI? Answered by the aggregate of the five §3 sections; determines whether §6.4's retraction check costs one call or two.

## 11. Acceptance criteria

- [ ] `README.md` publishes all 12 queries verbatim, the cell-record schema, and the provenance note, and is approved before any API contact
- [ ] All 60 cells populated; no cell blank or marked "not attempted"
- [ ] C1 returns a hit for every connector, or the failure is diagnosed as a harness fault and fixed before that dossier is accepted
- [ ] C2 returns zero hits for every connector, or the non-empty result is recorded as a finding in that dossier's §7
- [ ] Each dossier's §3 states, per connector, whether item-level venue classification is possible
- [ ] Each dossier ends in an unambiguous bind / wrap / drop recommendation
- [ ] `06-tier-model.md` contains no psychology-specific rule in Axes A or B, the resolution order, or the retraction and preprint handling
- [ ] `DECISION.md` answers AGE-548 question 3 with a stated rationale
- [ ] `DECISION.md` §7.4 gives applyable deltas — literal file content, not descriptions
- [ ] `DECISION.md` §7.5 names every capability the plugin will still lack after the deltas are applied
- [ ] No file outside `docs/research/connectors/` is modified by this effort

---

## Appendix A — Verification basis

Claims in §1 and §6.1 were verified by direct read on 2026-08-15:

| Claim | Verified against |
|---|---|
| `.mcp.json` is `{"mcpServers": {}}` | `psychology-research/.mcp.json` (26 bytes) |
| `bio-research` declares five HTTP servers | `bio-research/.mcp.json` |
| `literature: []`, Tier-2 wires `[pubmed, semantic-scholar, ~~web]` | `skills/psychology-evidence-builder/SKILL.md:5` |
| Semantic Scholar preferred for modality/qualitative/book canon | `skills/psychology-evidence-builder/SKILL.md:30`; `CONNECTORS.md:13`; `references/modality-canon.md` |
| `source-tiers.yaml` is a flat 31-entry domain map | `references/source-tiers.yaml` |
| Six `UNRESOLVED` results; four of eight lenses ungrounded | `hci-canon` `research/vibrancy-runs/2026-08-14-don-lila/literature-grounding.md` |
| Untiered-domain count; silent-skip behaviour; locator and paradigm failures | `docs/2026-08-13-diagnosis-counseling-findings-and-plugin-backlog.md` §3.4, citing `source_tiers_loader.py:43-44` and `source_tier_minimum.py:74-79` |
| `bio-research` has no validators | `docs/2026-08-13-...md` appendix — recursive listing, no `scripts/` directory |
| Consumer/producer source-list and lens-count contradictions | `hci-canon` `.claude/skills/relational-vibrancy/SKILL.md:70`, `:86`, frontmatter |
| Version history of the empty connector surface | `hci-canon` `docs/superpowers/research/2026-08-14-age-542-premise-audit.md` §3 |

**Not verified.** Whether a public MCP server exists for any of the five candidates; whether Semantic Scholar, OpenAlex, Crossref, Europe PMC, or PsyArXiv/OSF is reachable keyless; whether APA PsycNET has any programmatic route. These are the research questions, not assumptions this specification rests on.
