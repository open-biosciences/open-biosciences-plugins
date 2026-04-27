# Fuzzy-to-Evidence Protocol

Fuzzy-to-Evidence adapts Fuzzy-to-Fact for psychology, psychotherapy, sex therapy, family systems, and provider-fit research. The core discipline is: discover candidates from fuzzy language, retrieve source material, extract claims, classify evidence quality, then synthesize with explicit limits.

This is research support only: not diagnosis, not therapy, not medical advice, and not a substitute for licensed care.

## Workflow

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | LOCATE | Find candidate sources, concepts, providers, credentials, or guidelines from fuzzy input |
| 2 | RETRIEVE | Open or query the source directly; prefer official, primary, or peer-reviewed sources |
| 3 | EXTRACT | Pull only claim-sized facts with source URL, title, publisher, and retrieval date |
| 4 | CLASSIFY | Label each claim by evidence level and source tier |
| 5 | SYNTHESIZE | Answer the question using only extracted claims; mark gaps explicitly |
| 6 | REPORT | Format a sourced report or provider-fit matrix |
| 7 | REVIEW | Check attribution, overclaiming, stale facts, and clinical-safety language |

## Evidence Packet

Commands and skills should pass around this shape in conversation or files:

```json
{
  "question": "string",
  "mode": "research | provider_fit | report_review",
  "entities": [
    {
      "name": "string",
      "type": "concept | modality | credential | provider | organization | guideline | local_context",
      "status": "VERIFIED | SELF_REPORTED | SUPPORTED | UNRESOLVED | CONFLICTING",
      "notes": "string"
    }
  ],
  "claims": [
    {
      "claim": "string",
      "status": "VERIFIED | SELF_REPORTED | SUPPORTED | UNRESOLVED | CONFLICTING",
      "source_ids": ["S1"],
      "source_tier": "primary | secondary | tertiary | local_context",
      "limitations": "string"
    }
  ],
  "sources": [
    {
      "id": "S1",
      "title": "string",
      "publisher": "string",
      "url": "string",
      "retrieved_at": "YYYY-MM-DD",
      "source_tier": "primary | secondary | tertiary | local_context"
    }
  ],
  "evidence_levels": {
    "VERIFIED": "Confirmed by official, primary, licensing, credentialing, guideline, or peer-reviewed source.",
    "SELF_REPORTED": "Claim appears on provider/practice/commercial directory material but lacks official verification.",
    "SUPPORTED": "Credible research or professional source supports the concept, but not as an individualized clinical conclusion.",
    "UNRESOLVED": "No adequate source after reasonable search attempts.",
    "CONFLICTING": "Sources disagree; report the conflict rather than guessing."
  },
  "limitations": ["string"],
  "retrieved_at": "YYYY-MM-DD"
}
```

Provider mode adds:

```json
{
  "provider_credentials": [],
  "licensure_checks": [],
  "modality_claims": [],
  "fit_matrix": [],
  "contact_questions": []
}
```

## Source Hierarchy

| Tier | Examples | Use |
|------|----------|-----|
| Primary/official | State licensing boards, certifying bodies, professional organizations, clinical guidelines, peer-reviewed papers | Required for current provider/license facts and high-stakes clinical claims |
| Secondary/self-reported | Provider websites, Psychology Today, TherapyDen, Zencare, practice pages | Useful for modality claims, style, logistics, and first-contact questions; label `SELF_REPORTED` unless independently verified |
| Tertiary/contextual | Blogs, news, Reddit, marketing pages, summaries | Context only; never sufficient for high-stakes claims |
| Local context | User docs, local memory files, project concepts | User-provided thesis/context; not external evidence |

## Provider Verification Rules

- Verify licensure through the relevant jurisdiction's licensing board when possible.
- Verify AASECT, ICEEFT, AEDP Institute, Somatic Experiencing International, EMDRIA, IFS Institute, or similar credentials through the certifying body when possible.
- Date-stamp all current provider facts with `retrieved_at`.
- If a provider page says "EFT trained" but ICEEFT does not verify certification, label the claim `SELF_REPORTED` or "training claim, not certification."
- Do not simulate real clinicians. Do not generate in-character therapist responses from provider profiles.

## Crisis Routing

If user content suggests acute self-harm, suicide risk, active abuse, or psychiatric emergency, pause research framing, name 988 for US crisis support, and encourage immediate local emergency or licensed-professional help.
