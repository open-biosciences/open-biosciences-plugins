---
description: Quality-review a psychology research or provider-fit report against an evidence packet
argument-hint: "<report path and evidence packet path | use conversation context>"
---

# Psychology Research: Quality Review

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

You are running a quality review using the `psychology-quality-review` skill. This evaluates source attribution, evidence labels, provider verification, clinical-safety language, stale current facts, and hallucination risk.

## Usage

```
/psy-review $ARGUMENTS
```

Where `$ARGUMENTS` includes a report path and evidence packet path, or `use conversation context`.

## Workflow

### Step 1: Gather Artifacts

Read in order:
1. Evidence packet
2. Report
3. Referenced local context docs, if needed

Do not review the report alone if an evidence packet exists. The packet is the source of truth for whether evidence was actually retrieved.

### Step 2: Identify Report Type

Classify as:
- Concept/modality research
- Provider-fit report
- Narrative psychology review
- Mixed report

### Step 3: Score Review Dimensions

Score each dimension as `PASS`, `PARTIAL`, `FAIL`, or `N/A`:

| Dimension | Check |
|-----------|-------|
| Source attribution | Factual claims cite evidence packet sources |
| Evidence labels | `VERIFIED`, `SELF_REPORTED`, `SUPPORTED`, `UNRESOLVED`, and `CONFLICTING` are applied correctly |
| Source hierarchy | High-stakes claims rely on primary/official or peer-reviewed sources |
| Provider verification | License and certification facts are live-verified and date-stamped where possible |
| Current-fact freshness | Provider availability, licensure, telehealth, and contact facts include `retrieved_at` |
| Local vs external evidence | User docs are not treated as external evidence |
| Clinical safety | Report says not therapy, not diagnosis, and not medical advice |
| Crisis routing | Crisis/self-harm content routes to 988 and pauses analysis |
| Real-person boundary | Report does not simulate real clinicians |
| Hallucination risk | Unsupported diagnoses, prescriptions, rankings, or invented facts are flagged |

### Step 4: Classify Failures

For each issue, classify root cause:
- Evidence gap
- Presentation gap
- Overclaim
- Safety issue
- Stale current fact
- Provider-verification gap

### Step 5: Return Review

Return:
- Overall verdict: `LOW`, `MEDIUM`, or `HIGH` risk
- Dimension table
- Highest-severity findings first
- Required fixes
- Optional improvements
