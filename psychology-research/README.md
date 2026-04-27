# Psychology Research Plugin

Run evidence-grounded psychology research and therapist/provider fit assessment with source hierarchy, claim provenance, clinical-safety guardrails, and evidence-graded reports.

This plugin adapts the Open Biosciences Fuzzy-to-Fact discipline to psychology, therapy, and provider-fit workflows. It is intentionally a Markdown-only v1: commands, skills, and references, with no bundled MCP servers, scripts, validators, or runtime services.

## What's Included

### Connectors

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](CONNECTORS.md).

| Category | Placeholder | What It Does |
|----------|-------------|--------------|
| Literature | `~~literature` | Finds peer-reviewed and professional psychology sources |
| Web search/browser | `~~web` | Finds current provider pages and public source material |
| Licensing board | `~~licensing board` | Verifies state licensure and disciplinary status |
| Certifying body | `~~certifying body` | Verifies AASECT, ICEEFT, AEDP, SE, EMDRIA, IFS, and similar claims |
| Clinical guidelines | `~~clinical guidelines` | Grounds treatment/modality claims in official guidance |
| Graph memory | `~~graph memory` | Optional persistence or retrieval of prior evidence packets |

### Skills

| Skill | What It Does |
|-------|--------------|
| **psychology-evidence-builder** | Runs `LOCATE -> RETRIEVE -> EXTRACT -> CLASSIFY -> SYNTHESIZE` for psychology and therapy research questions |
| **psychology-provider-fit** | Verifies provider fit, credentials, licensure, modality claims, location, telehealth, and referral gaps |
| **psychology-reporting** | Formats sourced reports from evidence packets with evidence labels and safety language |
| **psychology-quality-review** | Reviews reports for source attribution, overclaiming, clinical safety, stale provider facts, and hallucination risk |

### Commands

| Command | What It Does |
|---------|--------------|
| `/psy-research` | Run evidence-grounded psychology research from a question or document |
| `/psy-provider` | Verify therapist/provider fit, credentials, modality claims, and gaps |
| `/psy-report` | Format a sourced report from an evidence packet |
| `/psy-review` | Quality-review a report and evidence packet |

## Common Workflows

**Evidence-Grounded Research**
Use `/psy-research` for questions about attachment theory, AEDP, EFT, RSD, chronic pain, sex therapy, family systems, narrative psychology, or related domains. The command separates local thesis/context from external evidence.

**Provider Fit**
Use `/psy-provider` on a provider name, criteria list, or local provider profile. It classifies facts as `VERIFIED`, `SELF_REPORTED`, `SUPPORTED`, `UNRESOLVED`, or `CONFLICTING`.

**Report And Review**
Use `/psy-report` to format a sourced report, then `/psy-review` to check evidence quality, safety language, and provider-verification gaps.

## Safety

This plugin is research support, not medical advice, not therapy, and not diagnosis. It must not diagnose, prescribe, rank a clinician as clinically best, or simulate real clinicians. If acute self-harm, suicide risk, or psychiatric crisis appears, route to 988 and pause analysis.

## License

Skills are licensed under Apache 2.0. External tools and directories are provided by their respective authors.
