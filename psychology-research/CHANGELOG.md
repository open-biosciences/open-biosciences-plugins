# Changelog

All notable changes to the `psychology-research` plugin are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-07-09

### Added
- **Graph-memory fragment contract** (`references/graph-memory-contract.md`): a tool-agnostic JSON schema for supplying graph-stored context to a research run as `local_context` evidence — a graph-sourced fact is context local to the effort, never external `VERIFIED` evidence.
- **`graph_memory_fragment` validator** (`scripts/validators/graph_memory_fragment.py`) with a runnable CLI (`python3 scripts/validators/graph_memory_fragment.py <file>`) and unit tests: enforces that every fragment is `type: local_context`, carries the required edge fields, and is never labeled `VERIFIED`.
- **`~~graph-memory` fragment-file input** documented in `CONNECTORS.md` and cross-linked from the evidence Source Hierarchy in `references/fuzzy-to-evidence.md`.

## [0.1.0]

### Added
- Initial Tier-1a release: the reference layer, the publish gate with seven validators, and the `/psy-*` commands and skills.
