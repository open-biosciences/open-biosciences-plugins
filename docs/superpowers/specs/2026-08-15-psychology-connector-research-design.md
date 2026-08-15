# psychology-mcp Layer-1 discovery: connector research and the literature envelope

**Date:** 2026-08-15
**Status:** Draft (rev 2) — awaiting maintainer review
**Layer:** 1 (SpecKit discovery) — produces the `research.md` inputs for a Layer-2 build
**Deliverable location:** `docs/research/connectors/` (relocates to `psychology-mcp` when that repo exists — see §3.4)

**Tickets:** unblocks [AGE-552]; answers question 3 of [AGE-548]; consumer-side context in [AGE-542], [AGE-559], [AGE-560]; informs [AGE-554].

> **Revision note.** Rev 1 scoped this effort to the plugin layer — "which URLs go in `psychology-research/.mcp.json`." That was the wrong layer. `bio-research` declares `biosciences-mcp` and `biosciences-mcp-edge`, which are **first-party servers built by this program**, not third-party endpoints. `psychology-research/.mcp.json` is empty because psychology has **no Layer-2 implementation to point at**. Rev 2 retargets the same research at its correct consumer. Rev 1's four factual errors are listed in Appendix C.

---

## 1. Problem

`psychology-research` ships `.mcp.json` as `{"mcpServers": {}}` — unchanged across 0.1.0, 0.2.0, and 0.2.1 — and `skills/psychology-evidence-builder/SKILL.md` declares `bindings: literature: []`. Literature retrieval falls through to `~~web` and is tier-capped below `VERIFIED`.

The cost is measured, not hypothesised. On 2026-08-14 a consumer run bound a PubMed MCP server in-session and executed the evidence-builder procedure. Six research questions returned `UNRESOLVED`, and the run's own diagnosis was explicit:

> These six are a **binding limitation, not an absence of literature.** … for modality theory, qualitative practice literature, or book-form canon, prefer Semantic Scholar or state the paradigm fit. No Semantic Scholar connector is bound in this session, and PubMed's own scope note excludes non-medical psychology.

**The underlying cause is structural.** The life-sciences half of the platform has a complete stack: SpecKit discovery produced 13 API specifications, which became 12 FastMCP servers plus a gateway in `biosciences-mcp`, which the `bio-research` plugin declares and its skills consume. The psychology half has Layers 1, 3, and 4 — governance intent, a plugin manifest, and four skills — and nothing at Layer 2.

A second problem compounds it, and rev 1 placed it in the wrong layer too. `references/source-tiers.yaml` is a flat `domain → integer` map of 31 entries; `lookup_tier()` returns `None` on a miss and `validators/source_tier_minimum.py` **skips any source it cannot tier**. One real run cited 25 domains absent from the map. The plugin is scraping tier signal out of URL strings because nothing upstream hands it structured bibliographic metadata. Under ADR-001 that normalization is a **Layer-2 responsibility** — the literature analog of the Agentic Biolink `cross_references` mandate.

These are one problem: **psychology has no server layer, so the plugin improvises metadata it should be given.**

## 2. Where this sits in the platform

```
Layer 1  SpecKit discovery      ADRs 001–006 · research.md → spec.md → plan.md → tasks.md
              ↓                  ← THIS SPEC
Layer 2  FastMCP implementation biosciences-mcp (12 servers + gateway) · psychology-mcp (MISSING)
              ↓                  deployed to fastmcp.app
Layer 3  Plugin manifest        open-biosciences-plugins/*/.mcp.json → gateway URL
              ↓
Layer 4  Skills                 bio-research/* · psychology-research/* · relational-vibrancy (external consumer)
```

`lifesciences-research` was Layer 1 before the org migration; it became `biosciences-mcp` + `biosciences-program`. Its `research.md` artifacts are the template this specification follows.

### 2.1 Governing ADRs

Read from `biosciences-mcp/docs/adr/accepted/`. A `psychology-mcp` inherits these; where an ADR is biomedical-specific, the psychology adaptation is stated.

| ADR | Mandate | Adaptation for literature |
|---|---|---|
| **001 §2** Hybrid client | Strict async `httpx` for modern APIs; `run_in_executor` only for legacy sync SDKs, which **must** then expose batch tools | All five candidates are REST/JSON — expect strict async throughout, no executor exception |
| **001 §3** Fuzzy-to-Fact | Phase 1 accepts natural language → ranked candidates; Phase 2 accepts **only** resolved CURIEs; raw string to a strict tool returns `UNRESOLVED_ENTITY` | `search_works(query)` → ranked candidates; `get_work(doi)` accepting only a resolved DOI. **The DOI is the CURIE.** The protocol transfers without strain |
| **001 §4** Agentic Biolink | Flattened JSON; every entity response **must** carry a `cross_references` object per the Key Registry | Vocabulary is bibliographic, not Biolink. Requires a **literature Key Registry** (§6.3) |
| **001 §5** Tool/Resource bifurcation | Tools return JSON capped at 50 items; Resources return raw text via custom URI schemes | Full text is a Resource (`work://fulltext/{doi}`), not a Tool payload |
| **001 §6** Triangulation | High-stakes assertions verified across `cross_references` | A work found in two indexes with agreeing DOIs is triangulated; single-index-only is a recorded weakness |
| **001 §7** Token budgeting | Batch tools **must** accept `slim=True`; default page size 50 | Slim fields defined in §6.4. ADR-001's slim triple is `id`/`name`/`score`; literature needs its own |
| **001 §8** Canonical envelopes | Exact pagination and error envelope shapes | Adopted verbatim — these are protocol, not domain |
| **001 §9** Shared vs domain types | Protocol types must not import domain types | `CrossReferences` and envelopes are protocol; `Work`, `Venue` are domain |
| **002** | Platform skills (`scaffold-fastmcp`) over manual coding | Server scaffolding uses the platform skill |
| **003** | SpecKit SDLC | This spec is the `/specify` input; per-API specs follow |
| **004** | Module-level singleton lifecycle; `@mcp.on_event` **forbidden** | Adopted as-is |
| **005** | Git worktrees for 3+ parallel servers | Applies to the Layer-2 build, not to this discovery pass |
| **006** | Single-writer `clients/` package | Adopted as-is |

**Layer discipline.** `psychology-mcp` is a Python ≥3.11 package with real dependencies (`fastmcp`, `httpx`, `pydantic`, `uv.lock`), mirroring `biosciences-mcp`. `psychology-research` remains a lightweight plugin — manifest, markdown skills, and a `.mcp.json` pointing at the deployed gateway. These are different artifacts with different rules; conflating them is the error rev 1 made.

## 3. Scope

### 3.1 In scope

- Five connector dossiers: **Semantic Scholar, OpenAlex, Crossref, Europe PMC, PsyArXiv/OSF**.
- A live coverage probe of all five against a **pre-registered 12-query benchmark** (§4).
- The **literature envelope design** (§6): venue class, the literature Key Registry, slim fields, retraction and preprint handling — specified as the Layer-2 response contract per ADR-001 §4 and §8.
- One decision document (§7): the `psychology-mcp` server roster and build order, the AGE-548 q3 answer, and the interim plugin binding.

### 3.2 Out of scope

- **Building `psychology-mcp`.** This is Layer-1 discovery. The build is a separate SpecKit program, one `/specify` per server.
- Creating the `psychology-mcp` repository (§3.4 records the open decision).
- Changes to `psychology-research` skills, commands, or validators.
- Changes to `bio-research` or `biosciences-mcp`.
- Changes to `hci-canon`. Contradictions found there (§7.3) are recorded, not fixed.
- Applying any delta. `DECISION.md` proposes; a separate PR applies.

### 3.3 Deliverables

All under `docs/research/connectors/`:

| File | Contents |
|---|---|
| `README.md` | Method, the frozen benchmark, cell-record schema, how to re-run |
| `00-coverage-matrix.md` | 5 APIs × 12 queries = 60 cells, with example records |
| `01-semantic-scholar.md` … `05-psyarxiv-osf.md` | Dossiers (§5 template) |
| `06-literature-envelope.md` | The Layer-2 response contract (§6) |
| `DECISION.md` | Server roster, build order, AGE-548 q3, interim binding, limitations (§7) |

### 3.4 Where `psychology-mcp` lives — decided

**`/home/donbr/open-biosciences/psychology-mcp`** — sibling of `biosciences-mcp`, inside the workspace defined by `open-biosciences.code-workspace`. Created 2026-08-15 (empty). The earlier placeholder at `/home/donbr/hci/psychology-mcp`, which sat outside the workspace, has been deleted.

Still open, and deferred to the Layer-2 program (Appendix B): whether it becomes a git repository under the `open-biosciences` GitHub org alongside the other 13, and whether it is added to the workspace file and the platform README's repository table.

This specification and its deliverables **relocate into that repo** once it is initialised. Until then they live in `open-biosciences-plugins` on `feat/psychology-connector-research`. Note that repository is itself cloned into three roots — see [AGE-567]; the authoritative WSL checkout for this work is `/home/donbr/hci/open-biosciences-plugins`.

### 3.5 Candidate rationale

| Candidate | Why included |
|---|---|
| **Semantic Scholar** | The plugin's own declared Tier-2 binding, named in `CONNECTORS.md`, `SKILL.md` twice, and `modality-canon.md`. Broad disciplinary coverage including a citation graph |
| **OpenAlex** | Broadest open scholarly index; covers humanities, books, and non-biomedical psychology. Keyless |
| **Crossref** | DOI registry including monographs and book chapters. **The authoritative source for `venue_class` and retraction status** — §6 depends on it structurally, not merely for coverage |
| **Europe PMC** | Candidate **replacement** for a PubMed binding rather than an addition. Its REST API exposes full-text XML, preprints, and NCBI Bookshelf monographs alongside PubMed records. Supersede-vs-complement is a research finding, not an assumption |
| **PsyArXiv / OSF Preprints** | The psychology preprint server. Occupies the slot bioRxiv was wrongly proposed for; bioRxiv is molecular and cell biology. Routes via OSF API v2 as `/v2/preprints/?filter[provider]=psyarxiv`; where those preprints carry Crossref DOIs, cross-checking §3 metadata against `03-crossref.md` measures how well preprint metadata survives across indexers |

**Considered and deferred, recorded so they are not re-litigated:**

- **APA PsycNET / PsycINFO** — the canonical psychology index. Believed licensed with no open API. **Note that credentialed access is not a packaging blocker**: `.mcp.json` supports `${VAR}` expansion in `headers`, `headersHelper` for connect-time header generation, and plugin `userConfig` with `sensitive: true`. If PsycNET is programmatically reachable at all, it is declarable. `DECISION.md` §7.5 must state the consequence if it is not, because `source-tiers.yaml` assigns `apa.org: 1`.
- **ERIC** — education, counselling, school psychology. Relevant under the general-purpose framing; second pass.
- **medRxiv, Unpaywall, DOAJ, CORE, Internet Archive / Open Library** — each narrower than the five. Internet Archive is the known route to historical primaries (Q5) and is revisited if no selected connector resolves it.
- **bioRxiv** — rejected. Wrong domain.

## 4. The benchmark suite

Twelve queries: ten measuring coverage, two controls. Frozen before any API is contacted.

**Pre-registration is the point.** The coverage matrix is intended as citable evidence and as the acceptance suite for the Layer-2 build. Queries chosen after seeing what an API returns are not evidence. Q1–Q8 derive from a gap list recorded 2026-08-14, before any connector was under consideration; Q9–Q10 were added during design to close a subject-axis blind spot, also before any API contact. This provenance is recorded in `README.md`.

Two independent axes. **Format** — does the connector index this kind of artefact. **Subject** — does it reach this discipline's publisher ecosystem. A benchmark strong on one and blind to the other selects connectors that look uniformly excellent and then underperform.

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

**Q6 note.** PubMed returned only *fledgling*-relationship literature here. The query is deliberately scoped to established dyads to preserve that discrimination.

**C1 is scored separately** from the coverage cells. It validates the harness — a connector that misses it has a broken client, not a coverage gap — and is not counted toward any coverage score.

**C2 is a fabricated construct with a fabricated citation.** It exists because fabricated citations have already reached a user-facing surface in this ecosystem (AGE-547). Scoring requires a distinction, because "zero results" is the wrong bar: token-relevance engines will return topically adjacent work by matching individual words (`co-regulation`, `index`) even when the construct does not exist. That is normal retrieval, not a defect.

| Outcome | Score | Record |
|---|---|---|
| Zero results | **pass** | `result: miss`, `n_results: 0` |
| Non-empty, no construct match — adjacent papers only | **pass** | `result: miss`, `n_results: N`, note *"token search returned adjacent papers; no construct match"* |
| A result presented as matching the fabricated construct or citation | **fail** | Finding in that dossier's §7 |

The failure mode under test is a **confident exact match for something that does not exist**, not breadth of recall.

### 4.1 Cell record schema

Each of the 60 cells records:

| Field | Values |
|---|---|
| `result` | `hit` / `partial` / `miss` |
| `n_results` | integer |
| `top_result` | title, authors, year |
| `venue_class` | one of §6.2 |
| `doi_present` | boolean |
| `metadata_completeness` | which of the §6.3 registry keys and §6.2 fields the API actually returned |
| `notes` | free text |

`metadata_completeness` is the load-bearing field. A connector that returns results but no venue type **cannot support the §6 envelope**, which is a first-order selection criterion independent of coverage.

## 5. Dossier template

Each `0N-<api>.md` uses this fixed structure so the five are comparable.

| § | Content |
|---|---|
| 1 | **Identity and access** — base URL, auth model, key requirement, published and observed rate limits, ToS and attribution obligations. *(Non-trivial: the PubMed connector already imposes a DOI-link attribution requirement. Assume each has its own until verified.)* |
| 2 | **Mechanics** — request/response format, pagination model, filtering, batch support, error behaviour |
| 3 | **Item metadata** — what the API returns per record, mapped against the §6.3 literature Key Registry and the §6.2 venue classes. **This section is the input to §6.** |
| 4 | **Measured coverage** — this API's 12 cells with example records |
| 5 | **Fuzzy-to-Fact feasibility (ADR-001 §3)** — can it support `search_works` → ranked candidates and `get_work(doi)` strict retrieval? Does it accept a DOI as a lookup key? |
| 6 | **FastMCP wrapping feasibility (ADR-001 §2, §7)** — async-native REST or a sync SDK needing `run_in_executor`; batch endpoint availability; rate limits under agent concurrency; whether slim mode is expressible |
| 7 | **Existing MCP server** — does one exist, keyless or credentialed, maintainer, currently live. *Determines whether we wrap or bind.* |
| 8 | **Recommendation** — wrap in `psychology-mcp` / bind an existing server / drop, with reasoning and residual risk |

Sections 5 and 6 are the additions rev 1 lacked. A connector's value is not only what it finds, but whether it can be made to conform to the platform's protocol.

## 6. The literature envelope

ADR-001 §4 mandates that every entity response carry a `cross_references` object per a Key Registry, and §8 fixes the pagination and error envelopes. The biomedical instance of that is Agentic Biolink. Literature needs its own instance, and **this is where venue classification belongs** — not in the plugin's `source_tiers_loader.py`, which is scraping URL strings for signal that a conformant server would hand it directly.

### 6.1 The two axes, relocated

**Axis A — venue class.** *What the item is.* Resolved server-side from registered bibliographic metadata.
**Axis B — discovery route.** *Which connector surfaced it.* Recorded for provenance and triangulation (ADR-001 §6). **Never contributes to tier.**

An index is a lookup vehicle, not a peer-review warrant. Tiering `api.openalex.org` would tier a consumer-media blog post as peer-reviewed because OpenAlex indexed it.

### 6.2 Venue classes

`peer-reviewed-article` · `book` · `book-chapter` · `institute-publication` · `preprint` · `guideline` · `grey` · `commentary` · `unverified`

Resolution order, server-side:

1. **DOI with registered metadata** → classify from the item's own registered `type`, venue, and publisher. Locator domain irrelevant. *This is the locator-vs-source fix, structural rather than an exception list.*
2. **No DOI** → the envelope reports `venue_class: unverified` with the source URL, and the consumer falls back to its domain map.
3. **Neither** → `unverified`, which the consumer **must warn on**, never silently skip. *This is the vacuous-pass fix.*

Two properties fall out once the server holds registered metadata:

- **Retraction status is an envelope field**, not a consumer inference. Crossref exposes retraction and update notices; a retracted work is flagged at the source. This is the highest-value integrity check available to research output.
- **Preprint is its own class**, not a downgraded article — resolving the article-plus-its-own-preprint double count.

**Paradigm overrides stay at Layer 4.** "For topic X, institute publications are the canonical evidence base" is a psychology-research editorial judgement expressed in `modality-canon.md`, not a property of a work. The server reports what a thing *is*; the plugin decides what that is *worth* for a given claim. Keeping this split is what makes the envelope reusable by consumers with different editorial policies.

### 6.3 Literature Key Registry

The bibliographic analog of ADR-001 Appendix A. Every work response carries `cross_references` with whichever of these resolve:

`doi` · `pmid` · `pmcid` · `openalex_id` · `semantic_scholar_id` · `osf_id` · `arxiv_id` · `isbn` · `issn`

Null-handling and cardinality follow ADR-001 Appendix A. Two connectors returning agreeing DOIs for one work is a triangulation success under ADR-001 §6; single-index-only provenance is a recorded weakness.

### 6.4 Slim mode

ADR-001 §7 mandates `slim=True` on batch tools and specifies `id`/`name`/`score` for biomedical entities. Literature needs its own slim triple, proposed as **`doi`, `title`, `venue_class`** — enough for an agent to triage relevance and admissibility without pulling abstracts. Default page size 50 per §5.

`06-literature-envelope.md` specifies the full contract; per-API conformance is assessed in each dossier's §3.

## 7. The decision document

`DECISION.md` carries five sections.

**7.1 Server roster and build order.** Which APIs `psychology-mcp` wraps, in what tier order, rolled up from each dossier's §8 — the psychology analog of the biosciences Tier 0–5 table. Plus which, if any, are better bound as existing third-party servers than wrapped.

**7.2 AGE-548 question 3.** *Does the plugin own MCP server declarations, or does the consumer supply them?* The in-repo precedent answers it, correctly read this time: `bio-research` declares **its own program's gateway** (`biosciences-mcp`, `biosciences-mcp-edge`) plus a small number of public third-party servers (`pubmed`, `biorxiv`, `synapse`). The pattern is **"the plugin declares the platform's first-party gateway, and public third-party servers where they exist."** Credentialed access is not the boundary — `${VAR}` header expansion, `headersHelper`, and `userConfig`/`sensitive` all exist. `psychology-research`'s `.mcp.json` is empty because the first-party gateway does not exist yet, and the interim question is which third-party servers to declare while it is built.

**7.3 Producer/consumer contradictions found during research.** Recorded, not fixed:

- `hci-canon` `.claude/skills/relational-vibrancy/SKILL.md:70` names `pubmed-database / OpenAlex / Europe PMC`; `psychology-research` names `pubmed, semantic-scholar`. Consumer and producer disagree.
- The same file's frontmatter enumerates seven modalities plus an eighth lens, `SKILL.md:86` says *"omit to run all seven"*, and the 2026-08-14 run report says *"four of the eight lenses."*

**7.4 Interim plugin binding.** The concrete `.mcp.json` delta for what can be declared **today**, before `psychology-mcp` exists. **Written out, not applied.** Every entry must carry `"type": "http"` — an entry with a `url` and no `type` is read as stdio, skipped, and warned about. Note that `psychology-research/` is mirrored downstream into `psychology-research-plugins` by `rsync --delete`; deltas must be authored upstream and reach the mirror by that sync, never hand-edited there.

**7.5 What remains unsatisfiable.** Stated plainly. At minimum: if no connector reaches APA/PsycINFO-class content, `source-tiers.yaml` assigning `apa.org: 1` and the marketplace description promising *"source hierarchy, claim provenance"* both describe reach the plugin cannot deliver. Any connector with partial coverage gets its partiality named rather than averaged away.

## 8. Execution sequence

1. **Freeze.** Write `README.md` with the 12 queries, the cell-record schema, and the provenance note. **Maintainer approves before any API is contacted.** This gate is what makes the benchmark pre-registered rather than retrospective.
2. **Dossiers, one API at a time**: Semantic Scholar → OpenAlex → Crossref → Europe PMC → PsyArXiv/OSF. Each complete (template §1–§8, including its 12 cells) before the next begins.
3. **Assemble** `00-coverage-matrix.md` from the five dossiers' §4.
4. **Write** `06-literature-envelope.md`, informed by the aggregated §3 metadata findings.
5. **Write** `DECISION.md`.
6. **Stop.** The Layer-2 build is a separate SpecKit program; applying the interim binding is a separate PR.

**Parallelism.** Steps 1 and 6 are gates and run inline. Step 2's five dossiers are independent units — separate adapter, test, fixture, results file, and dossier each — and are dispatched **in parallel, one agent per connector**, per ADR-005 ("we adopt Git Worktrees as the canonical pattern for parallel MCP server development"; its Phase 0 namespace refactor removes the one shared write, the connector registry). Steps 3–5 need all five complete and run inline.

Parallel dispatch is conditional on **artefact-level verification, not agent reports**: a connector's work is accepted only when its recorded fixture is a genuine API payload and its twelve cell records pass `validate()`. See the plan's fan-out protocol.

*(Rev 1 asserted "no agent fan-out for artefact production" here and the plan then cited this section as its authority — a fabricated constraint with a circular citation. Corrected 2026-08-15; see Appendix C item 5.)*

## 9. Non-goals

- Building `psychology-mcp` or any FastMCP server.
- Creating the `psychology-mcp` repository.
- Reconciling `bio-research` or `biosciences-mcp` to anything here.
- Fixing the `hci-canon` contradictions in §7.3.
- Applying any delta to `.mcp.json`, `CONNECTORS.md`, or `source-tiers.yaml`.
- Re-opening AGE-548 beyond its question 3.
- Any change to `psychology-research`'s crisis-safety surface, evidence-label vocabulary, or `local_context` tier rule. These are settled and reusable as-is.

## 10. Risks and open questions

| Risk | Mitigation |
|---|---|
| Probe results reflect query phrasing rather than coverage | Two axes per query, positive and negative controls, phrasing frozen and published |
| The envelope design outruns the discovery evidence | §6 is written *after* the five dossiers' §3, not before |
| Q5 (1928 primary source) resolves in none of the five | Expected. Internet Archive / Open Library revisited in a second pass; the honest finding goes in `DECISION.md` §7.5 |
| Rate limits make 60 cells slow or throttled | Dossier §1 establishes limits before probing; probes sequential per API, not parallel |
| Scope drifts from discovery into building a server | §3.2 and §9 both name it; §8 step 6 is an explicit stop |
| Deliverables authored into the wrong checkout of a repo cloned three times | §3.4 names the authoritative WSL checkout; tracked as [AGE-567]. This already happened once during rev 1 |

**Open questions carried into execution:**

1. Does Europe PMC supersede a PubMed binding, or complement it? Answered by `04-europe-pmc.md` §4 and §7.
2. Is APA PsycNET reachable by any programmatic route? A bounded check in `DECISION.md` §7.5, not a sixth dossier.
3. Does any connector expose retraction status directly, or is Crossref a required second lookup per DOI? Answered by the aggregate of the five §3 sections; determines whether §6.2's retraction field costs one call or two.
4. Can one gateway serve all five, or do rate limits force separate servers? Informs the §7.1 build order.

## 11. Acceptance criteria

- [ ] `README.md` publishes all 12 queries verbatim, the cell-record schema, and the provenance note, and is approved before any API contact
- [ ] All 60 cells populated; no cell blank or marked "not attempted"
- [ ] C1 returns a hit for every connector, or the failure is diagnosed as a harness fault and fixed before that dossier is accepted
- [ ] C2 produces no construct match for any connector, scored per the §4 table
- [ ] Each dossier's §3 states which §6.3 registry keys and §6.2 fields that API actually returns
- [ ] Each dossier's §5 and §6 state Fuzzy-to-Fact and FastMCP-wrapping feasibility explicitly
- [ ] Each dossier ends in an unambiguous wrap / bind / drop recommendation
- [ ] `06-literature-envelope.md` conforms to ADR-001 §4, §7, §8 and §9, and cites each
- [ ] `06-literature-envelope.md` contains no consumer editorial policy — paradigm overrides stay at Layer 4
- [ ] `DECISION.md` §7.1 gives a server roster with build order
- [ ] `DECISION.md` §7.2 answers AGE-548 q3 from the first-party-gateway precedent
- [ ] `DECISION.md` §7.4 gives an applyable interim delta — literal file content, every entry carrying `"type": "http"`
- [ ] `DECISION.md` §7.5 names every capability still lacking after the interim delta
- [ ] No file outside `docs/research/connectors/` is created or modified

---

## Appendix A — Verification basis

Verified by direct read on 2026-08-15:

| Claim | Source |
|---|---|
| `.mcp.json` is `{"mcpServers": {}}` | `psychology-research/.mcp.json` (26 bytes) |
| `bio-research` declares 5 servers, 2 first-party | `bio-research/.mcp.json`; `biosciences-program/README.md` repository table |
| `literature: []`; Tier-2 wires `[pubmed, semantic-scholar, ~~web]` | `skills/psychology-evidence-builder/SKILL.md:5` |
| Semantic Scholar preferred for modality/qualitative/book canon | `SKILL.md:30`; `CONNECTORS.md:13`; `references/modality-canon.md` |
| `source-tiers.yaml` is a flat 31-entry domain map | `references/source-tiers.yaml` |
| Six `UNRESOLVED`; four of eight lenses ungrounded | `hci-canon` `research/vibrancy-runs/2026-08-14-don-lila/literature-grounding.md` |
| Untiered-domain count; silent-skip behaviour | `docs/2026-08-13-…-plugin-backlog.md` §3.4, citing `source_tiers_loader.py:43-44`, `source_tier_minimum.py:74-79` |
| ADR mandates in §2.1 | `biosciences-mcp/docs/adr/accepted/adr-001-v1.4.md` §§2–9; adr-002 … adr-006 |
| 12 servers + gateway; Python ≥3.11 with fastmcp/httpx/pydantic | `biosciences-mcp/src/biosciences_mcp/servers/`; `biosciences-mcp/pyproject.toml` |
| Platform layer roles and migration lineage | `biosciences-program/README.md`; `open-biosciences.code-workspace` |
| Plugin architecture: bundled code, dependency mechanisms, `${VAR}` expansion, `headersHelper`, `userConfig`, `url`-needs-`type` | `code.claude.com/docs/en/plugins-reference`; `code.claude.com/docs/en/mcp` |
| Consumer/producer contradictions | `hci-canon` `.claude/skills/relational-vibrancy/SKILL.md:70`, `:86`, frontmatter |

**Not verified.** Whether a public MCP server exists for any of the five; whether each is reachable keyless; whether APA PsycNET has any programmatic route; the actual response shape of any candidate API. These are the research questions, not assumptions this spec rests on.

## Appendix B — Deferred to the Layer-2 program

Recorded so the discovery pass does not absorb them: initialising `psychology-mcp` as a git repository under the `open-biosciences` org, and adding it to `open-biosciences.code-workspace` and the platform README repository table (the directory exists per §3.4; the repo does not); per-API SpecKit specs under ADR-003; the gateway design and whether one server or several; deployment to fastmcp.app; the `psychology-research/.mcp.json` delta pointing at the deployed gateway; `bio-research` adoption of the literature envelope where it overlaps (PubMed, bioRxiv) under AGE-554.

## Appendix C — Rev 1 errors

Recorded because each came from inference rather than reading a source, and the pattern matters more than the individual mistakes.

1. **Misread the `bio-research` precedent.** Rev 1 read all five declared servers as third-party and concluded "the plugin owns keyless public servers; the consumer owns credentialed." Two are first-party. The real pattern is first-party gateway plus selected public servers.
2. **Invented a stdlib-only constraint** from the absence of `pyproject.toml` in the plugin repo. Plugins do not declare Python dependencies by design; the Layer-2 package has real ones.
3. **Assumed plugins cannot bundle executable code.** `scripts/`, `bin/`, and `skills/*/scripts/` are documented features, which also means AGE-554's "expose validators via `bin/`" asks for an existing capability.
4. **Placed venue classification at Layer 4.** ADR-001 §4 and §8 put schema normalization in the server envelope. The plugin was scraping URLs for signal a conformant server would supply.
5. **Fabricated an execution constraint and cited itself for it.** §8 asserted "no agent fan-out for artefact production"; the implementation plan then cited §8 as the authority. Nothing supported it. The belief was imported from a memory scoped to the storyboard pipeline, whose own text disclaims the generalization ("this does not condemn subagents generally"), and whose failure mode was forged output rather than parallelism. **ADR-005 mandates the opposite** for 3+ similar units. Corrected: dossiers fan out; verification is by artefact, not by report.
