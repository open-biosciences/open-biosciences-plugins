"""Publish-gate orchestrator.

Loads the validator registry, runs each validator against the input report,
assembles a bundle (report.md + evidence-packet.json + manifest.json + content-hash.txt),
and writes it to the output directory.

Usage:
  python3 scripts/publish.py <report-path> --out <bundle-dir>

The orchestrator does not block on publish itself; it records the overall severity
in the manifest. The slash command surface (`/psy-publish`) presents the manifest to
the user; users decide whether to ship despite warnings or fix and re-run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from scripts.validators import REGISTRY, Severity, ValidatorResult


@dataclass(frozen=True)
class BundlePaths:
    report: Path
    evidence_packet: Path
    manifest: Path
    content_hash: Path


def _overall_severity(results: list[ValidatorResult]) -> Severity:
    if any(r.severity is Severity.BLOCK for r in results):
        return Severity.BLOCK
    if any(r.severity is Severity.WARN for r in results):
        return Severity.WARN
    return Severity.PASS


def _hash_bundle(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: x.name):
        h.update(p.name.encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


# Status footers for the bundled report copy.
#
# `/psy-report` emits the unvalidated-draft watermark, which is true of its
# output and false the moment this gate finishes. The bundle copy therefore
# carries a footer derived from the gate result rather than one asserted by
# the report's author: a computed status line cannot go stale.
#
# Edit the wording here; it is the single source for all three outcomes.
_DRAFT_WATERMARK_MARKER = "STATUS: UNVALIDATED DRAFT"

_STATUS_FOOTERS = {
    Severity.PASS: (
        "STATUS: VALIDATED \u2014 publish gate passed. See manifest.json for "
        "per-validator results and content-hash.txt for the bundle digest."
    ),
    Severity.WARN: (
        "STATUS: VALIDATED WITH WARNINGS \u2014 publish gate returned WARN. "
        "Review the findings in manifest.json before distributing."
    ),
    Severity.BLOCK: (
        "STATUS: BLOCKED \u2014 publish gate returned BLOCK. This report is "
        "not for distribution; see manifest.json for the blocking findings."
    ),
}


def _apply_status_footer(text: str, overall: Severity) -> str:
    """Replace the draft watermark with the footer the gate result warrants.

    A report carrying no watermark is returned unchanged: the gate reports
    status, it does not invent one for a report that never claimed any.
    """
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if _DRAFT_WATERMARK_MARKER in line:
            trailing = "\n" if line.endswith("\n") else ""
            lines[i] = _STATUS_FOOTERS[overall] + trailing
            return "".join(lines)
    return text


def run_gate(report_path: Path, out_dir: Path,
             evidence_packet_path: Path | None = None) -> BundlePaths:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run all registered validators.
    results: list[ValidatorResult] = []
    for v in REGISTRY:
        try:
            results.append(v(report_path))
        except UnicodeDecodeError as exc:
            results.append(ValidatorResult(
                name=getattr(v, "__name__", "unknown"),
                severity=Severity.BLOCK,
                findings=[
                    f"{report_path} is not valid UTF-8 (byte "
                    f"{exc.object[exc.start]:#04x} at position {exc.start}). "
                    "Re-save the report as UTF-8 and re-run the gate."
                ],
            ))
        except Exception as exc:
            results.append(ValidatorResult(
                name=getattr(v, "__name__", "unknown"),
                severity=Severity.BLOCK,
                findings=[f"validator raised: {exc!r}"],
            ))

    overall = _overall_severity(results)

    # Assemble bundle artifacts. The report is rewritten rather than copied so
    # its status footer reflects this gate run (see _apply_status_footer).
    bundle_report = out_dir / "report.md"
    bundle_report.write_text(
        _apply_status_footer(report_path.read_text(encoding="utf-8"), overall),
        encoding="utf-8",
    )

    bundle_packet = out_dir / "evidence-packet.json"
    if evidence_packet_path and evidence_packet_path.exists():
        shutil.copyfile(evidence_packet_path, bundle_packet)
    else:
        bundle_packet.write_text("{}", encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_source": str(report_path),
        "overall": overall.value,
        "validators": [
            {"name": r.name, "severity": r.severity.value, "findings": r.findings}
            for r in results
        ],
    }
    bundle_manifest = out_dir / "manifest.json"
    bundle_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True),
                               encoding="utf-8")

    # Hash includes report, packet, manifest (in that order, sorted by name).
    digest = _hash_bundle([bundle_report, bundle_packet, bundle_manifest])
    bundle_hash = out_dir / "content-hash.txt"
    bundle_hash.write_text(digest + "\n", encoding="utf-8")

    return BundlePaths(
        report=bundle_report,
        evidence_packet=bundle_packet,
        manifest=bundle_manifest,
        content_hash=bundle_hash,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--evidence-packet", type=Path, default=None)
    args = parser.parse_args()

    paths = run_gate(args.report, args.out, args.evidence_packet)
    manifest = json.loads(paths.manifest.read_text())
    sys.stdout.write(json.dumps(manifest, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if manifest["overall"] != "BLOCK" else 1


if __name__ == "__main__":
    sys.exit(main())
