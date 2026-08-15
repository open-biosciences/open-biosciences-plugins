# Changelog

All notable changes to the `psychology-research` plugin are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

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
