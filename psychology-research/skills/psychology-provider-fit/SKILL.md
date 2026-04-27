---
name: psychology-provider-fit
description: "Verify therapist or provider fit by checking licensure, credential claims, modality claims, telehealth/geography, source quality, and fit gaps. Use when the user mentions therapist search, provider fit, AASECT, ICEEFT, AEDP, licensing, clinician candidates, or provider profile review."
---

# Psychology Provider Fit

Assess therapist/provider fit with source hierarchy, date-stamped verification, and explicit limitations.

## Critical Grounding Rule

```
Provider fit is research support, not medical advice, not therapy, and not
diagnosis. Do not rank a clinician as clinically best. Do not simulate real
clinicians or generate in-character therapist responses from provider profiles.
```

## When To Use

- Reviewing a provider name, provider website, or local provider profile
- Checking AASECT, ICEEFT, AEDP, SE, EMDRIA, IFS, Gottman, PACT, or similar modality/credential claims
- Building fit matrices against user criteria
- Drafting first-contact questions

## Safety Preflight

- If acute self-harm, suicide risk, active abuse, or psychiatric crisis appears, name 988 and pause analysis.
- If jurisdiction is not clear, ask for it before verifying license facts.
- Default to California only when the input or local HCI docs imply California.

## Verification Workflow

### 1. Parse Criteria

Extract:
- Provider identity
- Jurisdiction
- Claimed license type
- Claimed credentials/certifications
- Claimed modalities
- Location and telehealth scope
- User's fit criteria

### 2. Verify Current Facts

Use strongest available sources:

| Claim Type | Preferred Source |
|------------|------------------|
| Licensure/status/discipline | `~~licensing board` |
| Certification | `~~certifying body` |
| Provider availability/contact/rates | Provider website or direct practice page via `~~web` |
| Commercial profile claims | Psychology Today, TherapyDen, Zencare, or similar via `~~web` |
| Modality relevance | `~~literature` or `~~clinical guidelines` |

All current facts need `retrieved_at`.

### 3. Classify Claims

- `VERIFIED`: official source confirms the claim
- `SELF_REPORTED`: provider/practice/commercial directory claims it, but official verification was not retrieved
- `SUPPORTED`: research/guideline support for the modality or fit criterion
- `UNRESOLVED`: no adequate source found
- `CONFLICTING`: sources disagree

### 4. Build Fit Matrix

Score fit qualitatively as:
- `Strong match`
- `Partial match`
- `Gap/referral needed`
- `UNRESOLVED`

Do not use "best clinician" language. Prefer "strongest documented match for [criterion]" or "most verified coverage among reviewed criteria."

## Output

```markdown
## Provider Fit Summary
[Research-support disclaimer]

## Verification Table
| Claim | Label | Source | Retrieved |
|-------|-------|--------|-----------|

## Fit Matrix
| Criterion | Fit | Evidence | Gap |
|-----------|-----|----------|-----|

## Contact Questions
1. ...

## Limits
- SELF_REPORTED: ...
- UNRESOLVED: ...
- CONFLICTING: ...
```

## Real-Person Boundary

Provider files describe real people with public practices. They are references, not prompts. Do not simulate real clinicians.
