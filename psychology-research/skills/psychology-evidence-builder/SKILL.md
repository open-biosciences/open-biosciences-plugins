---
name: psychology-evidence-builder
description: "Run evidence-grounded psychology, therapy, sex therapy, family-systems, or narrative-psychology research using LOCATE -> RETRIEVE -> EXTRACT -> CLASSIFY -> SYNTHESIZE. Use when the user asks to research a psychology concept, modality, clinical-adjacent thesis, or document with source provenance."
---

# Psychology Evidence Builder

Build sourced evidence packets for psychology and therapy research questions.

## Critical Grounding Rule

```
Do not answer clinical, provider, modality, or research claims from training
knowledge. Use retrieved sources, local user-provided context, or mark the claim
UNRESOLVED. This skill provides research support only: not therapy, not diagnosis,
not medical advice, and not a substitute for a licensed clinician.
```

## When To Use

- Researching concepts such as attachment theory, secure base, RSD, AEDP, EFT, IFS, chronic pain, sex therapy, or family systems
- Extracting evidence from a local document
- Separating a local thesis from external evidence
- Preparing an evidence packet for `/psy-report` or `/psy-review`

## When Not To Use

- Verifying a specific therapist/provider's licensure, credentials, or availability; use `psychology-provider-fit`
- Formatting a final report; use `psychology-reporting`
- Reviewing an existing report; use `psychology-quality-review`

## Safety Preflight

{{include: ../../references/crisis-resources.md}}

Before doing research:
- Do not diagnose or prescribe.
- Do not rank a clinician as clinically best.
- Do not simulate real clinicians.

## Fuzzy-to-Evidence Workflow

### 1. LOCATE

Find candidate sources from:
- `~~literature` for peer-reviewed or academic material
- `~~clinical guidelines` for professional guidance
- `~~web` for professional organizations, directories, or current public pages
- local files for user/context sources

Use multiple search attempts when needed. If no adequate source appears after reasonable attempts, mark the item `UNRESOLVED`.

### 2. RETRIEVE

Open or query the source directly. Prefer:
1. Official/licensing/certifying bodies
2. Peer-reviewed articles and professional guidelines
3. Provider websites and commercial directories
4. Contextual sources such as blogs, news, Reddit, or marketing pages

### 3. EXTRACT

Extract claim-sized findings only. Capture:
- Claim text
- Source title, publisher, URL, and `retrieved_at`
- Source tier
- Whether the claim is general research, current provider fact, or local context

### 4. CLASSIFY

Use these labels:
- `VERIFIED`: official, primary, licensing, credentialing, guideline, or peer-reviewed source confirms the claim
- `SELF_REPORTED`: provider/practice/commercial directory claim without official verification
- `SUPPORTED`: credible source supports the concept, not an individualized conclusion
- `UNRESOLVED`: adequate source not found
- `CONFLICTING`: sources disagree

### 5. SYNTHESIZE

Answer using extracted claims only. Keep interpretation visibly separate from evidence.

## Output

Return an evidence packet compatible with `references/fuzzy-to-evidence.md`, plus a compact summary:

```markdown
## Answer
[Synthesis from sourced claims]

## Evidence Packet Summary
| Claim | Label | Source Tier | Source |
|-------|-------|-------------|--------|

## Local Context vs External Evidence
[What came from local docs vs retrieved sources]

## Gaps
- UNRESOLVED: ...
- CONFLICTING: ...
```

## Important Limits

Local HCI docs are user/context sources, not external evidence. They may define the user's thesis but cannot verify external clinical, historical, provider, or scientific claims.
