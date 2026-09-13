---
description: "Validate a psychology-research draft report against the publish gate and emit a bundle (report + evidence packet + manifest + content hash)."
argument-hint: <draft-report-path> [--out <bundle-dir>]
---

# /psy-publish

Run the Tier-1 publish gate against a draft report and emit a bundle.

## Usage

```
/psy-publish <draft-report-path> [--out reports/<date>-<topic>/]
```

If `--out` is omitted, default to `reports/$(date +%Y-%m-%d)-<basename>/` relative to the current working directory.

## What this does

1. Invokes `python3 scripts/publish.py <draft-report-path> --out <bundle-dir>` via Bash from the plugin root.
2. The orchestrator runs the eight Tier-1 validators (see plugin docs §10):
   - citation (BLOCK)
   - source-tier-minimum (WARN)
   - forbidden-language (WARN)
   - crisis-trigger (BLOCK)
   - evidence-label-coverage (BLOCK)
   - bibliography-integrity (BLOCK)
   - template-conformance (BLOCK)
   - no-citations-found (BLOCK)
3. Writes the bundle: `report.md`, `evidence-packet.json`, `manifest.json`, `content-hash.txt`.
4. Presents the manifest summary to the user.

The bundled `report.md` is **not** a byte copy of the draft. Its unvalidated-draft
watermark is replaced with a footer derived from this run's `overall` severity, so a
bundle never carries a status line contradicting its own manifest. The draft on disk is
left untouched. The replacement happens before hashing, so `content-hash.txt` covers the
report as bundled.

If the manifest's `overall` field is `BLOCK`, the publish failed; surface the validator findings and stop. If `WARN`, surface the warnings and ask the user whether to proceed (the bundle is written either way; the user decides whether to share it).

## Implementation

This command is a thin wrapper. The validator suite is owned by `scripts/publish.py`. To add or remove a validator, edit the registry in `scripts/validators/__init__.py`, not this file.

## Safety

This command does not bypass the safety preamble in any constituent skill. Reports that include crisis-related content must still pass the crisis-trigger validator, which requires the `crisis-resources.md` content to be present byte-for-byte in the report.
