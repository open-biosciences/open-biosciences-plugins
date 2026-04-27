---
description: Verify therapist or provider fit, credentials, modality claims, location, licensure, and gaps
argument-hint: "<provider name | criteria | provider doc path>"
---

# Psychology Research: Provider Fit

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

You are assessing therapist/provider fit using the `psychology-provider-fit` skill and the provider mode of the Fuzzy-to-Evidence protocol.

## Usage

```
/psy-provider $ARGUMENTS
```

Where `$ARGUMENTS` is a provider name, criteria list, or local provider document path.

## Workflow

### Step 1: Parse Provider Input

Extract:
- Provider name and jurisdiction
- Claimed license type
- Claimed credentials and certifications
- Claimed modalities
- Location and telehealth scope
- User fit criteria

Default jurisdiction is California only when the input or local HCI docs imply California. Otherwise ask for jurisdiction before verifying license facts.

### Step 2: Safety Preflight

State that this is provider research support, not medical advice, not therapy, and not diagnosis.

Do not rank a clinician as clinically best. Do not simulate real clinicians. Do not generate in-character therapist responses from provider profiles.

If acute self-harm, suicide risk, active abuse, or psychiatric crisis appears, name 988 and pause analysis.

### Step 3: Verify Claims

Use the strongest available source for each claim:

1. Licensure: `~~licensing board`
2. Certifications: `~~certifying body`
3. Provider/practice claims: `~~web`
4. Research support for modality relevance: `~~literature` or `~~clinical guidelines`

Classify facts:
- `VERIFIED`: official source confirms it.
- `SELF_REPORTED`: provider or directory claims it, but no official verification was retrieved.
- `SUPPORTED`: literature/guidelines support the concept or modality in general.
- `UNRESOLVED`: not verified after reasonable search.
- `CONFLICTING`: sources disagree.

All current facts need `retrieved_at`.

### Step 4: Produce Provider Fit Matrix

Return:
- Verification summary
- Provider credentials and licensure checks
- Modality claims with source status
- Fit matrix against user criteria
- Gaps/referral needs
- Contact questions for first outreach
- Limitations and unresolved items

## Grounding Rule

Provider pages and commercial directories are useful but usually `SELF_REPORTED`. Do not promote them to `VERIFIED` without official confirmation.
