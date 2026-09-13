---
description: Format a sourced psychology research or provider-fit report from an evidence packet
argument-hint: "<evidence packet path | use conversation context>"
---

# Psychology Research: Report Formatting

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

You are formatting a sourced report using the `psychology-reporting` skill. This command consumes an evidence packet from `/psy-research`, `/psy-provider`, or conversation context.

## Usage

```
/psy-report $ARGUMENTS
```

Where `$ARGUMENTS` is an evidence packet path or `use conversation context`.

## Input

Required:
- Evidence packet with `question`, `mode`, `claims`, `sources`, `evidence_levels`, `limitations`, and `retrieved_at`

Provider mode additionally requires:
- `provider_credentials`
- `licensure_checks`
- `modality_claims`
- `fit_matrix`
- `contact_questions`

If the evidence packet is missing, ask the user to run `/psy-research` or `/psy-provider` first.

## Workflow

### Step 1: Load Evidence Packet

Validate required fields from [references/fuzzy-to-evidence.md](../references/fuzzy-to-evidence.md). Report missing fields and do not invent them.

### Step 2: Select Template

Use the report mode:
- Concept/modality research
- Provider-fit report
- Narrative psychology research
- Safety/clinical-risk review
- Mixed report

### Step 3: Format Report

Include:
- Research support disclaimer: not therapy, not diagnosis, not medical advice
- Direct answer or fit summary
- Claims table with evidence labels
- Source table with source tier and retrieval date
- Local context vs external evidence
- `UNRESOLVED` and `CONFLICTING` gaps
- Practical next questions or next research step

### Step 4: Preserve Limits

Do not add new facts during reporting. Use only the evidence packet. If the report needs missing data, mark it `UNRESOLVED`.

## Required output footer

Every `/psy-report` output ends with the **unvalidated-draft watermark**, emitted verbatim as the final line:

> `STATUS: UNVALIDATED DRAFT — citation tiers, evidence labels, and language filters not yet checked. Run /psy-publish to validate and persist.`

`/psy-report` runs none of the publish-gate validators, so this line is the only thing distinguishing a rendered draft from a validated one. Do not write a validated-sounding status here: `/psy-publish` replaces this line in the bundle copy with a footer derived from the gate result.

Do **not** emit a `PLUGIN VERSION NOTICE` banner. The Tier-1a banner declaring the literature MCP unwired was retired in 0.4.0 — `psychology-mcp` has been declared in `.mcp.json` since 0.3.0, and the banner had been understating the plugin's own provenance since. `template_conformance` BLOCKs any report that reintroduces it.

If the report's primary modality is identified during analysis and is **not** present in `references/modality-canon.md`, also emit the **Tier-1b banner** before the watermark footer:

> `PARADIGM ROUTING NOTICE: modality '<name>' is not yet mapped in modality-canon. Preferred-source guidance unavailable; literature retrieval will use general defaults and may surface paradigm-mismatched results.`
