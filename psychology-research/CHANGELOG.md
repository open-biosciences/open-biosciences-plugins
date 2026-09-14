# Changelog

All notable changes to the `psychology-research` plugin are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

### Added
- `scripts/tests/test_declaration_consistency.py` — asserts that `.mcp.json` and the
  skills' frontmatter `bindings` agree, in both directions: a declared server must be
  bound by some skill or explicitly exempt, and no skill may bind a server the runtime
  does not declare. Also fails if a skill's prose describes an already-declared
  connector as pending. Fourth instance of declaration drift (AGE-723); first guard
  that catches the class rather than an instance.

### Decided
- `psychology-mcp` is **deliberately not bound** in any skill's `bindings.literature`,
  and is recorded in that module's `INTENTIONALLY_UNBOUND` with the reason and date.
  It supplies registration metadata (DOI, `venue_class`, `classification_basis`,
  `retraction_status`), not claim content, and whether a metadata-only route may raise
  a claim's evidence tier is an open design question. Binding it alongside a
  claim-content connector would pre-decide that by flattening the distinction.
  The exemption and the binding are now enforced to change together.

### Fixed
- `psychology-evidence-builder/SKILL.md` no longer describes `psychology-mcp` coverage
  as pending ("arrives with"), nor — as a first correction did — as landed, which
  contradicted the same section's "there is currently no bound connector". It now
  states the actual state: declared in `.mcp.json`, not bound in this skill.

## [0.4.0] - 2026-09-12

### Removed
- **The Tier-1a banner is retired.** `/psy-report` prefaced every report with `PLUGIN VERSION NOTICE: literature MCP not yet wired; claims grounded in web search and local context only. Citation tiers above SUPPORTED unavailable for literature claims.` That was accurate when it was written (2026-04-28, commit `52f5b17`) and became false on 2026-08-15 when `psychology-mcp` was declared in `.mcp.json` (commit `2dfb829`, AGE-587). `commands/psy-report.md` was not touched by that PR, so for the **29 days** between the wiring landing and this release, every report **understated its own provenance** — telling readers that DOI-resolved, `classification_basis: registered` results were web-grounded, and that tiers above `SUPPORTED` were unavailable when they were not. The banner's own text said it would be removed "once the `~~literature` MCP wiring lands"; the wiring landed and the removal did not.

### Added
- **`template_conformance` now checks the report's status lines**, the gap that let the banner go unchecked for its whole 138-day lifetime — including the 29 days it was false. The validator's canonical-pass fixture had carried neither banner nor watermark and still passed, so nothing in the suite could observe either line. It now BLOCKs on:
  - a **retired provenance banner** reappearing in a report (`RETIRED_BANNERS`, each entry annotated with the commit that made it true and the commit that falsified it);
  - a **missing unvalidated-draft watermark**;
  - a watermark that is **not the final line** — a footer a reader scrolls past warns nobody.
- **`scripts/publish.py` is runnable as documented.** `commands/psy-publish.md` has always specified `python3 scripts/publish.py <report> --out <bundle-dir>` from the plugin root, and that has never worked: running a file directly puts its own directory on `sys.path`, so the module-level `from scripts.validators import …` raised `ModuleNotFoundError: No module named 'scripts'`. The unit suite could not see it — pytest inserts the rootdir, so the import succeeded under test and failed for every real caller, which is how 40 tests passed over a CLI that could not start. Fixed with the same plugin-root bootstrap `scripts/validators/graph_memory_fragment.py` has carried since 0.2.0, rather than a second pattern.
- **`scripts/tests/test_cli_invocation.py`** (4 tests) runs both documented command lines as a subprocess with the plugin root as cwd and `PYTHONPATH` removed — the conditions a real caller has, and the only conditions under which this class of defect is visible. It pins the `graph_memory_fragment` bootstrap too, so the working sibling cannot silently regress.
- **`scripts/tests/test_report_status_line.py`** and **`scripts/tests/test_publish_status_footer.py`** (12 tests) covering the above and the derived footer below.

### Changed
- **The publish gate derives the bundled report's status footer instead of copying it.** `run_gate` previously did `shutil.copyfile`, so a validated bundle's `report.md` still read `STATUS: UNVALIDATED DRAFT — ... Run /psy-publish to validate and persist` after `/psy-publish` had already run. The bundle copy now carries `STATUS: VALIDATED` / `VALIDATED WITH WARNINGS` / `BLOCKED` derived from the manifest's `overall`. A status line computed at the moment the state is known cannot go stale the way an authored one does — which is the root cause of this release's bug, fixed at the mechanism rather than at the symptom. The draft on disk is left untouched, a report carrying no watermark is not given one, and the rewrite precedes hashing so `content-hash.txt` covers the report as bundled.
- **`psychology-provider-fit` no longer points at the retired banner.** `SKILL.md` told the model to accompany unbound `certifying-body` / `licensing-board` output with "the Tier-1a banner notice". Those categories are genuinely still unbound, so the disclosure is warranted — but the banner it named described the *literature* category. The skill now states the limitation in its own words.
- **`/psy-publish` documents eight validators, not seven.** The list had not been updated when `no_citations_found` was added in 0.3.0; `README.md` was corrected then, this command surface was not.

## [0.3.0] - 2026-08-16

### Added
- **`psychology-mcp` is declared in `.mcp.json`** — `https://psychology-mcp.fastmcp.app/mcp`, the platform's first-party Layer-2 gateway for psychology, the counterpart to `biosciences-mcp` in `bio-research`. It wraps Crossref, OpenAlex and Semantic Scholar behind two tools (`search_works`, `get_work`) and returns an explicit `venue_class` with the `classification_basis` that established it.

### Changed
- **The literature category is no longer PubMed-only.** `pubmed` is retained alongside for biomedical, psychiatric and RCT-shaped work; `psychology-mcp` is listed first, per the documented ordering (literature servers first, alphabetical within category).
- **`CONNECTORS.md` "What is bound today" rewritten.** It described a gap that no longer exists: the six paradigms a 2026-08-14 consumer run returned `UNRESOLVED` for — IFS, Somatic Experiencing / Sensorimotor, AEDP transformance, the Heroine's Journey, Marston DISC, and secure-base research in established adult dyads — **all return classified results**, verified 2026-08-16 against the deployed gateway. Marston's *Emotions Of Normal People* (1928) resolves as `book` / `registered`, the historical-primary case Crossref was selected for.
- **Semantic Scholar's roster row corrected.** It read *"not measured — Tier 2, unauthenticated API returns sustained HTTP 429, needs a key"*. The key was issued 2026-08-15 and the frozen benchmark re-run authenticated: **5 hit / 4 partial / 1 miss**, second only to Crossref (`DECISION.md` §1). It is Tier 1, and it is the only route to DOI-less records.

### Notes
- Two reading rules added to `CONNECTORS.md`, because more coverage makes over-claiming easier, not harder: `unverified` is a hit with an undecided class and must not be promoted to `VERIFIED`; and `retraction_status: unknown` means **not cleared**, never "not retracted".

## [0.2.1] - 2026-08-14

### Fixed
- **Crisis resources are reachable again.** All four skills carried a literal `{{include: ../../references/crisis-resources.md}}` in their Safety Preflight section. The expansion was a sync-time build step that was never run before publish, so the marker shipped as-is and no crisis content — 988 Suicide and Crisis Lifeline, SAMHSA, Crisis Text Line, Veterans Crisis Line, The Trevor Project, Trans Lifeline, RAINN, Childhelp — was present in the loaded skill text. The section read as though it were protected; it was not.

### Changed
- **Skills reference shared content by path instead of by build-step expansion**, matching how `bio-research` has always done it. Each Safety Preflight now states the crisis trigger condition and the two first-line US numbers inline, then links `references/crisis-resources.md` for the full list. One copy, read live, nothing to expand and nothing to drift.

### Removed
- `scripts/sync_expand.py`, `scripts/tests/test_sync_expand.py`, and `.github/workflows/marker-check.yml`. With no expansion step there is no marker for a gate to check. The workflow could not have caught the original bug in any case: it copied the tree, expanded the copy, then checked the copy, so it passed unconditionally.

## [0.2.0] - 2026-07-09

### Added
- **Graph-memory fragment contract** (`references/graph-memory-contract.md`): a tool-agnostic JSON schema for supplying graph-stored context to a research run as `local_context` evidence — a graph-sourced fact is context local to the effort, never external `VERIFIED` evidence.
- **`graph_memory_fragment` validator** (`scripts/validators/graph_memory_fragment.py`) with a runnable CLI (`python3 scripts/validators/graph_memory_fragment.py <file>`) and unit tests: enforces that every fragment is `type: local_context`, carries the required edge fields, and is never labeled `VERIFIED`.
- **`~~graph-memory` fragment-file input** documented in `CONNECTORS.md` and cross-linked from the evidence Source Hierarchy in `references/fuzzy-to-evidence.md`.

## [0.1.0]

### Added
- Initial Tier-1a release: the reference layer, the publish gate with seven validators, and the `/psy-*` commands and skills.
