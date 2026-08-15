"""Run one connector's 12 cells and write validated records to results/.

The registry below names all five connectors up front so that parallel
per-connector work never shares a write to this file (ADR-005 Phase 0).
Modules are imported lazily; a connector whose module is not yet written
fails only when it is run.
"""

from __future__ import annotations

import argparse
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .queries import QUERIES
from .schema import CellRecord, validate

# connector name -> module name under probe.connectors
CONNECTORS: dict[str, str] = {
    "semantic-scholar": "semantic_scholar",
    "openalex": "openalex",
    "crossref": "crossref",
    "europe-pmc": "europe_pmc",
    "psyarxiv-osf": "osf",
}

RESULTS_DIR = Path(__file__).parent / "results"


def load(name: str):
    module = importlib.import_module(f".connectors.{CONNECTORS[name]}", package="probe")
    if module.NAME != name:
        raise AssertionError(f"{CONNECTORS[name]}.NAME is {module.NAME!r}, expected {name!r}")
    return module


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _describe(item) -> str:
    authors = ", ".join(item.authors[:3]) or "unknown"
    return f"{item.title} — {authors} — {item.year}"


def run_connector(name: str) -> list[CellRecord]:
    module = load(name)
    records: list[CellRecord] = []

    for query in QUERIES:
        resp = module.search(query.search)
        top = resp.items[0] if resp.items else None
        rec = CellRecord(
            connector=name,
            query_id=query.id,
            result="hit" if top else "miss",
            n_results=resp.total,
            top_result=_describe(top) if top else None,
            venue_class="unverified",   # classified by hand per RUBRIC.md
            doi_present=bool(top and top.doi),
            metadata_completeness=(),   # filled in by hand per RUBRIC.md
            notes="",
            retrieved_at=_now(),
        )
        records.append(rec)
        print(f"{name} {query.id}: n={resp.total} top={rec.top_result}")

    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--connector", required=True, choices=sorted(CONNECTORS))
    args = parser.parse_args()

    records = run_connector(args.connector)

    # Validate the first pass. venue_class="unverified" and an empty
    # metadata_completeness are legitimate here — they are filled in by hand per
    # RUBRIC.md. This catches a broken adapter now rather than at refine time.
    problems = [(r.query_id, p) for r in records for p in validate(r)]
    for query_id, problem in problems:
        print(f"INVALID {query_id}: {problem}")
    if problems:
        raise SystemExit(f"{len(problems)} invalid record(s); not writing results")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{args.connector}.json"
    out.write_text(
        json.dumps([r.to_dict() for r in records], indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nwrote {out} ({len(records)} cells)")


if __name__ == "__main__":
    main()
