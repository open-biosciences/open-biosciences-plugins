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


def run_gate(report_path: Path, out_dir: Path,
             evidence_packet_path: Path | None = None) -> BundlePaths:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run all registered validators.
    results: list[ValidatorResult] = []
    for v in REGISTRY:
        try:
            results.append(v(report_path))
        except Exception as exc:
            results.append(ValidatorResult(
                name=getattr(v, "__name__", "unknown"),
                severity=Severity.BLOCK,
                findings=[f"validator raised: {exc!r}"],
            ))

    # Assemble bundle artifacts.
    bundle_report = out_dir / "report.md"
    shutil.copyfile(report_path, bundle_report)

    bundle_packet = out_dir / "evidence-packet.json"
    if evidence_packet_path and evidence_packet_path.exists():
        shutil.copyfile(evidence_packet_path, bundle_packet)
    else:
        bundle_packet.write_text("{}", encoding="utf-8")

    overall = _overall_severity(results)
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
