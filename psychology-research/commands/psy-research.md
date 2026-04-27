---
description: Run evidence-grounded psychology research from a question or document path
argument-hint: "<question | document path>"
---

# Psychology Research: Evidence Builder

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

You are running evidence-grounded psychology research using the `psychology-evidence-builder` skill and the Fuzzy-to-Evidence protocol in [references/fuzzy-to-evidence.md](../references/fuzzy-to-evidence.md).

## Usage

```
/psy-research $ARGUMENTS
```

Where `$ARGUMENTS` is a research question or a local document path.

## Workflow

### Step 1: Parse Input

If `$ARGUMENTS` is a file path, read the document and extract:
- Research questions
- Local thesis/context claims
- Named concepts, modalities, clinicians, credentials, populations, and risk topics

If `$ARGUMENTS` is a question, classify it as:
- Concept research
- Modality research
- Provider-fit support
- Narrative psychology research
- Report/review preparation

Local HCI docs are user/context sources, not external evidence.

### Step 2: Safety Preflight

Before research:
- If acute self-harm, suicide risk, active abuse, or psychiatric crisis appears, name 988 and pause research analysis.
- State that output is research support, not therapy, not diagnosis, and not medical advice.
- Do not diagnose, prescribe, rank a clinician as clinically best, or simulate real clinicians.

### Step 3: Run Fuzzy-to-Evidence

Use the `psychology-evidence-builder` skill:

1. LOCATE candidate sources through `~~literature`, `~~clinical guidelines`, or `~~web`.
2. RETRIEVE source material directly.
3. EXTRACT claim-sized findings with source metadata and retrieval dates.
4. CLASSIFY each claim as `VERIFIED`, `SUPPORTED`, `SELF_REPORTED`, `UNRESOLVED`, or `CONFLICTING`.
5. SYNTHESIZE only from extracted evidence.

For current provider/license facts, delegate to `/psy-provider` or the `psychology-provider-fit` skill.

### Step 4: Present Results

Return:
- Direct answer
- Evidence packet summary
- Claim table with source labels
- What is local thesis vs external evidence
- `UNRESOLVED` gaps
- Suggested next command: `/psy-report` or `/psy-review`

## Grounding Rule

Do not fill gaps from training knowledge. If adequate evidence is not retrieved, mark the item `UNRESOLVED`.
