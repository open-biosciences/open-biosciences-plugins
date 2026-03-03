# Plugin Review: bio-research

**Review Date**: 2026-03-03
**Reviewer**: Claude Code (automated review against official plugin structure standards)
**Plugin Path**: `bio-research/`
**Reference Standard**: https://code.claude.com/docs/en/plugins-reference

---

## Structure Validation

### Official Claude Code Plugin Layout Requirements

Per the official docs, the standard plugin layout is:

```
plugin-root/
├── .claude-plugin/plugin.json   <- manifest (only file inside .claude-plugin/)
├── commands/                    <- at plugin root
├── skills/                      <- at plugin root
├── agents/                      <- at plugin root (optional)
├── hooks/                       <- at plugin root (optional)
├── .mcp.json                    <- at plugin root
└── README.md
```

### Component Validation Results

| Component | Expected Location | Actual Location | Status |
|-----------|------------------|-----------------|--------|
| Plugin manifest | `bio-research/.claude-plugin/plugin.json` | `bio-research/.claude-plugin/plugin.json` | PASS |
| Commands directory | `bio-research/commands/` | `bio-research/commands/` | PASS |
| Skills directory | `bio-research/skills/` | `bio-research/skills/` | PASS |
| MCP config | `bio-research/.mcp.json` | `bio-research/.mcp.json` | PASS |
| References directory | `bio-research/references/` | `bio-research/references/` | PASS (non-standard, supported) |
| CONNECTORS.md | `bio-research/CONNECTORS.md` | `bio-research/CONNECTORS.md` | PASS |
| LICENSE | `bio-research/LICENSE` | `bio-research/LICENSE` | PASS |
| Agents directory | not present | not present | N/A (optional) |
| Hooks directory | not present | not present | N/A (optional) |
| Repo-level marketplace | `.claude-plugin/marketplace.json` | `.claude-plugin/marketplace.json` | PASS |

**Overall structure verdict: PASS**

---

## What the Plugin Provides

### MCP Servers (from `bio-research/.mcp.json`)

| Server Name | Type | URL | Purpose |
|-------------|------|-----|---------|
| `biosciences-mcp` | http | https://biosciences-mcp.fastmcp.app/mcp | 34-tool gateway: HGNC, UniProt, STRING, BioGRID, ChEMBL, Open Targets, PubChem, IUPHAR, WikiPathways, ClinicalTrials.gov, Ensembl, Entrez |
| `biosciences-mcp-edge` | http | https://biosciences-mcp-edge.fastmcp.app/mcp | Edge tools: ORCS CRISPR essentiality, ChEMBL mechanism-of-action |
| `synapse` | http | https://mcp.synapse.org/mcp | Sage Bionetworks data repository |
| `pubmed` | http | https://pubmed.mcp.claude.com/mcp | PubMed literature |
| `biorxiv` | http | https://mcp.deepsense.ai/biorxiv/mcp | bioRxiv preprints |

**Total MCP servers**: 5

### Skills (from `bio-research/skills/`)

| Skill Directory | SKILL.md | LICENSE.txt | Status |
|-----------------|----------|-------------|--------|
| `biosciences-genomics` | Present | Present | Complete |
| `biosciences-proteomics` | Present | Present | Complete |
| `biosciences-pharmacology` | Present | Present | Complete |
| `biosciences-clinical` | Present | Present | Complete |
| `biosciences-crispr` | Present | Present | Complete |
| `biosciences-graph-builder` | Present | Present | Complete |
| `biosciences-reporting` | Present | Present | Complete |
| `biosciences-reporting-quality-review` | Present | Present | Complete |
| `biosciences-publication-pipeline` | Present | Present | Complete |
| `biosciences-cq-discover` | Present | Missing | Incomplete |
| `biosciences-cq-runner` | Present | Missing | Incomplete |

**Total skills**: 11 (9 original domain skills + 2 CQ beta skills)

### Commands (from `bio-research/commands/`)

| Command File | Frontmatter | Status |
|-------------|-------------|--------|
| `ob-research.md` | description + argument-hint | PASS |
| `ob-report.md` | description + argument-hint | PASS |
| `ob-review.md` | description + argument-hint | PASS |
| `ob-publish.md` | description + argument-hint | PASS |
| `ob-cq-discover.md` | description + argument-hint | PASS |
| `ob-cq-run.md` | description + argument-hint | PASS |

**Total commands**: 6

### References (from `bio-research/references/`)

| File | Purpose |
|------|---------|
| `fuzzy-to-fact.md` | Bi-modal LOCATE-RETRIEVE protocol documentation |
| `api-keys.md` | API key requirements and .env.example template |
| `token-budgeting.md` | `slim` parameter usage guide |

---

## Issues Found

### Important

**Issue 1: Hardcoded absolute path in `ob-cq-run.md` / `biosciences-cq-runner/SKILL.md`**

The skill hardcodes `/home/donbr/open-biosciences/biosciences-research/docs/competency-questions-catalog.md` as a fallback catalog path. This will fail for all users who are not the plugin author.

**Recommendation**: Replace with a relative path or `${CLAUDE_PLUGIN_ROOT}` reference.

**Issue 2: Skills count mismatch between README and actual content**

Both READMEs describe "Nine skills" but 11 skill directories exist. The 2 CQ skills (`biosciences-cq-discover`, `biosciences-cq-runner`) are not listed in the skills tables.

**Recommendation**: Update both READMEs to list all 11 skills.

**Issue 3: Missing `LICENSE.txt` in two skill directories**

`biosciences-cq-discover/` and `biosciences-cq-runner/` lack `LICENSE.txt` files, unlike all other 9 skills.

**Recommendation**: Add `LICENSE.txt` (Apache 2.0) to both directories.

### Minor

**Issue 4**: External notebook reference in `biosciences-crispr/SKILL.md` (`kg_rememberall/notebooks/...`) won't exist in installed contexts.

**Issue 5**: `plugin.json` missing optional `license` field. Add `"license": "Apache-2.0"`.

**Issue 6**: Top-level `README.md` links to `CONNECTORS.md` but file is at `bio-research/CONNECTORS.md`.

**Issue 7**: Inconsistent `/` prefix on CQ command names in README tables (other commands have `/`, CQ commands don't).

---

## Recommendations Summary

| Priority | Issue | Action |
|----------|-------|--------|
| Important | Hardcoded absolute path in cq-runner | Replace `/home/donbr/...` with relative reference |
| Important | Skills count says "nine" but 11 exist | Update READMEs to list all 11 skills |
| Important | Two skills missing LICENSE.txt | Add Apache 2.0 LICENSE.txt to CQ skill dirs |
| Minor | External notebook ref in crispr skill | Remove/rephrase reference |
| Minor | plugin.json missing license field | Add `"license": "Apache-2.0"` |
| Minor | Top-level CONNECTORS.md link broken | Update to `bio-research/CONNECTORS.md` |
| Minor | Inconsistent `/` prefix on CQ commands | Standardize formatting |

---

## Overall Assessment

The `bio-research` plugin is **structurally sound** against the official Claude Code plugin specification. The manifest, commands, skills, and MCP config are all in correct locations. The plugin provides a cohesive research workflow covering entity resolution, network expansion, drug discovery, clinical trials, validation, reporting, quality review, and publication.

The one issue that warrants attention before broad distribution is the hardcoded absolute filesystem path in `biosciences-cq-runner/SKILL.md`. All other findings are minor cleanup items.

*Review generated against: [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference)*
