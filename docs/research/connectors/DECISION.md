# DECISION — psychology-mcp server roster and interim binding

**Terminal artefact of the Layer-1 discovery pass.** Input to a Layer-2 SpecKit program.

**Date:** 2026-08-15 · **Spec:** [`../../superpowers/specs/2026-08-15-psychology-connector-research-design.md`](../../superpowers/specs/2026-08-15-psychology-connector-research-design.md)
**Evidence:** [`00-coverage-matrix.md`](00-coverage-matrix.md) · five dossiers · [`06-literature-envelope.md`](06-literature-envelope.md) · [`probe/CONTROLLER-NOTES.md`](probe/CONTROLLER-NOTES.md)

**This document proposes. It applies nothing.**

---

## 1. Server roster and build order

### Tier 0 — build first, jointly

These two are the minimum viable pair. Neither alone is sufficient, and the envelope
(§06) depends on both.

| | Verdict | Why it is Tier 0 |
|---|---|---|
| **Crossref** | **wrap** | Measured best: **8 hit / 2 partial / 0 miss**. The **only** connector reaching book canon (Murdock's *Heroine's Journey*) and historical primaries (Marston, **1928**). Sole source of `isbn`. Authoritative for `venue_class` — the envelope's Axis A rests on registered `type`, which is Crossref's own metadata. Keyless. |
| **OpenAlex** | **wrap** | The **only** connector supplying standing `retraction_status` (12/12 explicit boolean). Without it, `retraction_status` can only ever be `retracted` or `unknown`, never `not-retracted` (§06 ¶6). Also 12/12 on `publisher` and `type`. Keyless. |

**They are complements, not alternatives.** Crossref classifies; OpenAlex clears. Building
only Crossref means never being able to assert a work is *not* retracted. Building only
OpenAlex means losing book canon, `isbn`, and the registered-type authority the whole
classification scheme depends on.

### Tier 1 — build second

| | Verdict | Why |
|---|---|---|
| **Europe PMC** | **wrap** | Complements a PubMed binding rather than superseding it: 17.6% of sampled results (PMC + PPR) fall outside MEDLINE scope, and a preprint was top-ranked on 2 of 12 queries including the positive control. **Sole source of `pmcid`.** Its hits are Q9/Q10 — the quantitative and cognitive axis. Keyless. |

**Caveat carried forward:** Europe PMC **missed Q1–Q5 entirely.** It does not close the
modality, book-canon, or historical gap. Zero Bookshelf (`NBK`) records were observed
despite that being part of its candidate rationale — unconfirmed by this benchmark.

### Tier 2 — conditional, needs a decision first

| | Verdict | Note |
|---|---|---|
| **Semantic Scholar** | **wrap** — condition discharged | Key issued 2026-08-15; frozen benchmark re-run authenticated. **5 hit / 4 partial / 1 miss**, second only to Crossref. Remains the only **credentialed** connector — the other four completed keyless. |

Its metadata is the richest in the candidate set — DOI + PMID + CorpusId + ISSN in one
response, plus the only multi-prefix strict lookup (`DOI:`, `CorpusId:`, `PMID:`,
`ARXIV:`), which is exactly what the §4.2 "type but no DOI" records need.

**Done.** The key arrived, the frozen benchmark was re-run, and the result promotes it
from conditional to committed — but to **Tier 1, not Tier 0**. Tier 0 exists because the
envelope needs a classifier (Crossref) and a retraction clearer (OpenAlex). Semantic
Scholar supplies **neither**: `publisher` 0/12 and `retraction_status` 0/12. Excellent
coverage does not substitute for a Tier-0 responsibility.

**What earns it Tier 1 is unique reach, not rank.** It is the only connector to answer
Q3 (AEDP transformance, returning Fosha's own 2011 paper), and the only route to records
carrying no DOI — 3 of 12 top results, reachable solely via `CorpusId`.

**And it cannot classify its own best result.** The Q3 record carries no DOI, no type and
no venue, so the hit that justifies this connector arrives as `venue_class: unverified`,
`classification_basis: none`.

### Not in the roster

| | Verdict |
|---|---|
| **PsyArXiv/OSF** | **drop for search; revisit only for identifier-anchored retrieval.** Its `filter[title]` is a contiguous substring match, not an index — controller-verified: `filter[title]=couples` → 73 hits, `couples therapy` → 0. It cannot express the benchmark. It also exposes a silent no-op trap (a top-level `q=` returning HTTP 200 with identical results for real, nonsense, and absent queries) that a naive wrapper would ship as working search. |

**Its 0/10 is not a lost coverage contest** and must not be read as one.

### Build-order rationale

1. **Crossref + OpenAlex together** — the envelope is not implementable without both.
2. **Europe PMC** — additive coverage on a distinct axis, plus `pmcid`.
3. **Semantic Scholar** — only after a keyed re-run.
4. **PsyArXiv/OSF** — not scheduled.

### Bind vs. wrap

**No candidate should be bound to a third-party MCP server.** Community servers exist for
Crossref, OpenAlex and Semantic Scholar; every one found is unaffiliated, unverified live,
and several are dormant or archived. None exposes the envelope fields this design depends
on — venue class, `classification_basis`, retraction semantics. Binding one would place an
unmaintained third party in the path of the plugin's primary literature route, and for
Semantic Scholar would not even solve the constraint, which is upstream.

## 2. AGE-548 question 3 — does the plugin own MCP server declarations?

**Answer: yes, for the platform's own gateway and for public third-party servers.
Consumers are not expected to supply either.**

The in-repo precedent settles it. `bio-research/.mcp.json` declares five servers:

| Server | Nature |
|---|---|
| `biosciences-mcp` | **first-party** — this program's own deployed gateway |
| `biosciences-mcp-edge` | **first-party** |
| `pubmed` | third-party, public, keyless |
| `biorxiv` | third-party, public, keyless |
| `synapse` | third-party |

The pattern is **"the plugin declares the platform's first-party gateway, plus public
third-party servers where they exist."** Verified live: this session's tool surface
contains `mcp__plugin_bio-research_biosciences-mcp__*`, matching the documented scoped
form `mcp__plugin_<plugin>_<server>__<tool>`.

**`psychology-research/.mcp.json` is empty because the first-party gateway does not exist
yet** — not because connector ownership was ever assigned to the consumer.

### Credentialed access is not the boundary

Rev 1 of the spec argued *"plugin owns keyless public servers; consumer owns
credentialed."* **That is a false dichotomy.** Plugin-declared credentialed servers are
fully supported:

- `${VAR}` / `${VAR:-default}` expansion in `.mcp.json` — valid in `command`, `args`,
  `env`, `url`, `headers`
- `headersHelper` — a command run at connect time whose output is merged into headers
- plugin `userConfig` with `sensitive: true` — prompted at enable time, stored in keychain

So Semantic Scholar's API-key requirement does **not** exile it from the plugin. It
changes the **consumer contract** — key acquisition, storage, rotation — which is a real
adoption cost and belongs in the scope decision, but it is not a packaging barrier.

## 3. Producer/consumer contradictions found during research

Recorded, **not fixed** — both are in the downstream consumer repo, outside this effort's scope.

1. **Literature source list disagrees.** The downstream consumer skill
   names `pubmed-database / OpenAlex /
   Europe PMC`; `psychology-research` names `pubmed, semantic-scholar`. The consumer and
   the producer disagree about which non-PubMed source is intended. **This research
   supports the consumer's list**: OpenAlex and Europe PMC both measured; Semantic
   Scholar could not be measured.
2. **Lens count disagrees with itself.** The same file's frontmatter enumerates seven
   modalities plus an eighth lens; its body says *"omit to run all seven"*; the
   2026-08-14 run report says *"four of the eight lenses."*

## 4. Interim plugin binding — proposed, NOT applied

Until `psychology-mcp` exists, one connector can honestly be declared today: the
**already-proven, first-party, keyless PubMed server** that `bio-research` declares and
that is live in this session's tool surface.

Proposed `psychology-research/.mcp.json`:

```json
{
  "mcpServers": {
    "pubmed": {
      "type": "http",
      "url": "https://pubmed.mcp.claude.com/mcp"
    }
  }
}
```

**Every entry must carry `"type": "http"`.** An entry with a `url` and no `type` is read
as a stdio server, skipped at load, and warned about.

### What this delta does and does not do

**Does:** moves biomedical, psychiatric and RCT-shaped literature claims off `~~web`
fallback — where they are tier-capped below `VERIFIED` — onto a real connector. Changes
a consumer capability preflight from `plugin_web_supported` toward connector-grounded.

**Does not:** close the gap this effort exists to close. The 2026-08-14 run **already had
PubMed bound in-session** and still returned six `UNRESOLVED` results. PubMed's own scope
note excludes non-medical psychology. IFS, Somatic Experiencing / Sensorimotor,
Heroine's Journey and Marston DISC remain ungrounded until `psychology-mcp` ships
Crossref and OpenAlex.

Accompanying edits, same PR:

- **`CONNECTORS.md`** — replace *"Tier-1a ships with `mcpServers: {}`"* with the actual
  state, and record the roster and build order from §1.
- **`skills/psychology-evidence-builder/SKILL.md:5`** — `literature: []` becomes
  `literature: [pubmed]`; the `# Tier-2 wires [pubmed, semantic-scholar, ~~web]` comment
  should reflect that Semantic Scholar is unmeasured and credentialed.
- **`source-tiers.yaml`** — no change in this delta. Its redesign depends on the envelope
  (§06), which depends on `psychology-mcp` existing.

**Mirror discipline:** `psychology-research/` is mirrored downstream into
`psychology-research-plugins` by `rsync --delete`. Author upstream; let the sync
propagate. A hand-edit in the mirror is discarded by the next sync.

## 5. What remains unsatisfiable

Stated plainly, because the alternative is advertising capability that does not exist.

### 5.1 APA PsycNET — TESTED 2026-08-15. Not reachable, and the barrier is not authentication.

The deferral of PsycNET rested on an assumption ("licensed, no open API") that had never
been tested. It has now been, and the assumption holds — but for different reasons than
assumed, and with an important distinction the original framing missed.

| Probe | Result |
|---|---|
| `psycnet.apa.org/search/results?term=…` | **HTTP 403** |
| `psycnet.apa.org/api/search` | HTTP 200 — but returns the **Angular SPA shell**, not JSON. Not an API; the app serves `index.html` for unknown routes |
| `psycnet.apa.org/robots.txt` | **`User-agent: * / Disallow: /`** — only Googlebot, CrossrefEventDataBot, Twitterbot and bingbot are permitted, each to a narrow path list |
| APA licensing | *"All rights, including for text and data mining, AI training, and similar technologies, are reserved by APA"* |
| Sanctioned programmatic route | **PsycINFO Data Solutions** — a commercial custom-dataset service for subscribing institutions. Not a query API |

**The barrier is not credentials.** §2 establishes that credentialed servers are fully
declarable (`${VAR}`, `headersHelper`, `userConfig`/`sensitive`), so an API key would have
been no obstacle. There is **no API to authenticate against**, and automated access is
disallowed by `robots.txt` and by an explicit reserved-rights statement covering text
mining and AI training. A subscribing institution is in the same position as an
unsubscribed one with respect to a query interface.

**PsycNET is therefore removed from the candidate set — not deferred.** Revisit only if
APA publishes a query API.

### 5.1a The `apa.org: 1` tier entry is defensible; the implied capability is not

The original framing — *"`apa.org: 1` describes reach the plugin does not have"* — was too
broad. Two different surfaces were being conflated:

| Surface | Reachable? |
|---|---|
| **`www.apa.org`** — practice guidelines, policy statements, public pages | **Yes.** No catch-all `robots.txt` disallow; content pages return 200. Reachable today via `~~web` |
| **`psycnet.apa.org`** — the PsycINFO/PsycArticles bibliographic database | **No.** See above |

So `apa.org: 1` **stands** for APA's own published professional guidance, which is
legitimately Tier-1 authority and is fetchable now.

**What must be corrected is the implication that PsycINFO-class bibliographic search is
available.** Recommended `source-tiers.yaml` change, for the delta PR rather than this
document:

```yaml
apa.org: 1                 # APA's own published guidance — reachable via ~~web
psycnet.apa.org: 1         # authority tier is real, but NOT REACHABLE: no query API,
                           # robots-disallowed, TDM rights reserved. See DECISION.md 5.1
```

A tier entry for an unreachable source is not automatically wrong — the tier records
*authority*, not *access*. But a consumer that cannot distinguish "high tier, reachable"
from "high tier, unreachable" will plan retrievals that can never succeed. That
distinction belongs in the envelope's reachability metadata or in the tier file's
comments, and it is a live design question for the Layer-2 program.

### 5.2 Three venue classes are unresolvable from any connector

`guideline`, `institute-publication` and `commentary` have **no source type in any of the
four vocabularies**. `institute-publication` is the consequential one: it is defined by
*who published* the item, and it is exactly the AASECT / ICEEFT / AEDP / SE / EMDRIA /
IFS / Gottman / PACT tier in `source-tiers.yaml`. That tier has **no connector route**
and needs a Layer-4 publisher heuristic.

### 5.3 ~~One query no connector answers~~ — CLOSED

**Q3 — AEDP transformance is answerable after all.** The keyed Semantic Scholar re-run
returned Fosha's own *AEDP: Transformance In Action* (2011). Crossref's best remained a
`partial` on an APA PsycTherapy streaming-video catalogue entry typed `dataset`.

The correction is worth more than the win: Q3 was the sharpest evidence that
modality-theory literature was structurally unreachable. It was reachable — by the one
connector that could not be measured until a key was issued. **A capability gap and a
measurement gap looked identical from the outside**, and only the second one was real.

### 5.4 ~~Semantic Scholar's coverage is unknown~~ — RESOLVED

Measured at 5/4/1 on the keyed re-run. What remains is not uncertainty but cost: it is
the only roster connector requiring credentials, its granted rate is **1 req/s cumulative
across all endpoints** (MEASURED tighter than nominal — a 429 at 1.3s spacing, 2.5s needed
for sustained use), and its licence **requires attribution** in any published material,
an obligation that propagates to every downstream consumer of a grounded claim.

### 5.5 Partial coverage, named rather than averaged

| Connector | Named limitation |
|---|---|
| Crossref | No `oa_status`; retraction only in the affirmative; `dataset`→`grey` mapping is low-confidence, resting on one manually verified record |
| OpenAlex | `search=` is full-text token matching, not bibliographic relevance — the cause of all three of its misses (Q4 returned the phrase as a STEM-education metaphor; Q8 returned ecosystem-services literature). No `isbn` |
| Europe PMC | Missed Q1–Q5 entirely; no retraction field; `publisher` only 2/12; no Bookshelf records observed |
| PsyArXiv/OSF | Not an index |
| Semantic Scholar | Never supplies `publisher`; no retraction; unauthenticated tier unusable |

### 5.6 Unexercised and unverified

`arxiv_id` and `osf_id` were never returned by any connector — **unestablished, not
absent**. Europe PMC's `resultType=lite` slim mechanism is documented but unverified.
Semantic Scholar's strict lookup and `fields` projection rest on documentation and one
fixture. Terms-of-use and attribution obligations were not fully verified for any
connector.

---

## Next steps — none of which this document performs

1. **Interim binding PR** against AGE-552, applying §4.
2. **Semantic Scholar keyed re-run** — resolves §1 Tier 2 and §5.4.
3. ~~PsycNET reachability check~~ — **done 2026-08-15.** Not reachable; removed from the
   candidate set (§5.1). The follow-on is the `source-tiers.yaml` comment change in §5.1a,
   which folds into the interim binding PR.
4. **Layer-2 SpecKit program** — initialise `psychology-mcp` at
   `$OB_ROOT/psychology-mcp`, register it in
   `open-biosciences.code-workspace` and the platform README, then one
   `/speckit.specify` per server in §1 build order.
5. **`source-tiers.yaml` redesign** — follows the envelope, needs `psychology-mcp`.
6. **`bio-research` envelope adoption** where it overlaps (PubMed, bioRxiv) — AGE-554.
7. **Downstream consumer contradictions** (§3) — separate, in that repo.
