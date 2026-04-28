---
name: psychology-quality-review
description: "Review psychology research, therapy/provider-fit, or narrative-psychology reports for source attribution, evidence labels, provider verification, clinical-safety language, stale current facts, overclaiming, and hallucination risk."
bindings:
  literature: []    # Quality review may consult literature for cross-checking; populated at Tier-2.
  certifying-body: [~~certifying-body]
  licensing-board: [~~licensing-board]
  clinical-guidelines: [~~clinical-guidelines]
---

# Psychology Quality Review

Review psychology-research reports against their evidence packets.

## Critical Review Principles

```
Read the evidence packet before judging the report. Distinguish missing evidence
from presentation gaps. This is not diagnosis, not therapy, and not medical
advice. Do not simulate real clinicians.
```

## Resolution

Quality review may invoke the same bindings as `psychology-evidence-builder` to cross-check claims (literature spot-checks, credential re-verification). Use the bindings in priority order with the same fall-through semantics.

Quality review's primary outputs are reviewer findings — these are exempt from the publish-gate validators when the review is itself the artifact being produced. When the review's findings reference report claims with citations, follow the same evidence-label coverage discipline.

## Safety Preflight

{{include: ../../references/crisis-resources.md}}

## Required Reads

1. Evidence packet
2. Report
3. Local context docs, only if referenced

## Review Dimensions

Score each dimension as `PASS`, `PARTIAL`, `FAIL`, or `N/A`.

| Dimension | Check |
|-----------|-------|
| Source attribution | Factual claims cite evidence packet sources |
| Evidence labels | `VERIFIED`, `SELF_REPORTED`, `SUPPORTED`, `UNRESOLVED`, and `CONFLICTING` are applied correctly |
| Source hierarchy | High-stakes claims use primary/official, guideline, or peer-reviewed sources |
| Provider verification | Licensure and certification claims are official-source verified where possible |
| Current-fact freshness | Provider availability, license, telehealth, contact, and credential facts include `retrieved_at` |
| Local vs external evidence | User docs are not treated as external evidence |
| Clinical safety | Report says not therapy, not diagnosis, and not medical advice |
| Crisis routing | Crisis/self-harm content routes to 988 and pauses analysis |
| Real-person boundary | Report does not simulate real clinicians |
| Hallucination risk | Unsupported diagnoses, prescriptions, rankings, or invented facts are flagged |

## Failure Classes

- Evidence gap: evidence was not retrieved or is inadequate
- Presentation gap: evidence exists but the report omits or misstates it
- Overclaim: report exceeds source support
- Safety issue: report diagnoses, prescribes, gives emergency-inadequate advice, or misses 988 routing
- Stale current fact: provider/current fact lacks retrieval date or needs live verification
- Provider-verification gap: provider claim remains `SELF_REPORTED` or `UNRESOLVED`

## Verdict

Return overall risk:
- `LOW`: claims are sourced, labels are accurate, and safety boundaries are clear
- `MEDIUM`: some gaps or overstatements, but no major unsafe clinical claims
- `HIGH`: unsourced high-stakes claims, missing crisis handling, simulated clinician, diagnosis/prescription, or serious provider-verification failure

## Output

```markdown
## Overall Verdict
[LOW | MEDIUM | HIGH]

## Findings
| Severity | Dimension | Issue | Required Fix |
|----------|-----------|-------|--------------|

## Dimension Scores
| Dimension | Score | Rationale |
|-----------|-------|-----------|

## Residual Risk
[What remains unresolved after fixes]
```
