---
name: psychology-reporting
description: "Format sourced psychology research and provider-fit reports from evidence packets. Use when the user asks for a report, summary, writeup, fit matrix, evidence grading, or sourced synthesis after psychology/provider research."
bindings: {}    # Reporting consumes only the supplied evidence packet; no MCP retrieval at this stage.
---

# Psychology Reporting

Format professional reports from evidence packets without adding new facts.

## Grounding Rule

```
The report consumes an evidence packet. It does not retrieve new facts, invent
missing claims, diagnose, prescribe, or make clinical recommendations. Missing
evidence remains UNRESOLVED.
```

## Resolution

This skill consumes only the evidence packet handed to it from `/psy-research` or `psychology-evidence-builder`. It does **not** perform retrieval and does not invoke MCP servers. Bindings are intentionally empty.

Output must conform to the publish-gate template (see `commands/psy-publish.md` and `scripts/validators/template_conformance.py`): the sections **Answer**, **Evidence Packet Summary**, **Local Context vs External Evidence**, **Gaps**, **Sources** must appear in that canonical order. Every body claim sentence with a `[S\d+]` marker must carry an evidence label or the `(local synthesis)` annotation.

## Safety Preflight

{{include: ../../references/crisis-resources.md}}

## Required Input

Evidence packet fields:
- `question`
- `mode`
- `entities`
- `claims`
- `sources`
- `evidence_levels`
- `limitations`
- `retrieved_at`

Provider mode also needs:
- `provider_credentials`
- `licensure_checks`
- `modality_claims`
- `fit_matrix`
- `contact_questions`

## Templates

### Concept/Modality Research

Use for AEDP, EFT, attachment, RSD, chronic pain, sex therapy, family systems, narrative psychology, or similar topics.

Sections:
- Research support disclaimer
- Direct answer
- Key claims table
- Evidence synthesis
- Local context vs external evidence
- Gaps and limitations
- Sources

### Provider-Fit Report

Use for therapist/provider assessment.

Sections:
- Research support disclaimer
- Provider fit summary
- Verification table
- Fit matrix
- Referral or coverage gaps
- Contact questions
- Sources
- Limits

### Narrative Psychology Review

Use for HCI narrative documents, story/character systems, consent/safety governance, secure-base modeling, and voice/attachment rubrics.

Sections:
- Research support disclaimer
- Local thesis summary
- External evidence support
- Narrative-system implications
- Safety/consent notes
- Gaps and next research questions

## Required Language

Every report must include:
- "This is research support, not therapy, not diagnosis, and not medical advice."
- For crisis or self-harm content: 988 routing.
- For provider reports: "Provider pages and commercial directories may be SELF_REPORTED unless verified by official sources."

## Evidence Labels

Preserve labels exactly:
- `VERIFIED`
- `SELF_REPORTED`
- `SUPPORTED`
- `UNRESOLVED`
- `CONFLICTING`

## Do Not

- Do not add claims outside the evidence packet.
- Do not upgrade `SELF_REPORTED` to `VERIFIED`.
- Do not hide `UNRESOLVED` gaps.
- Do not rank a clinician as clinically best.
- Do not simulate real clinicians.
