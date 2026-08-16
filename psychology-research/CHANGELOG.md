# Changelog

All notable changes to the `psychology-research` plugin are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

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
