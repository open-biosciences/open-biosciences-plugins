"""The documented command lines actually run.

Both scripts are documented as directly runnable from the plugin root:

  python3 scripts/publish.py <report> --out <bundle-dir>          (psy-publish.md)
  python3 scripts/validators/graph_memory_fragment.py <file>      (graph-memory-contract.md)

Running a file directly puts its own directory on `sys.path`, not the plugin
root, so a bare `from scripts...` import raises ModuleNotFoundError. The unit
suite cannot observe this: pytest inserts the rootdir, so the import succeeds
under test and fails for every real caller. These tests therefore shell out
with the plugin root as cwd and PYTHONPATH removed, which is what a user has.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]

_CLEAN_REPORT = """\
# Report

## Answer
Relational turbulence theory is `VERIFIED` by the cited source. [S1]

## Evidence Packet Summary
One source.

## Local Context vs External Evidence
No local context.

## Gaps
None.

## Sources
- [S1] Solomon & Knobloch (2004). https://doi.org/10.1177/0265407504047838

STATUS: UNVALIDATED DRAFT — citation tiers, evidence labels, and language \
filters not yet checked. Run /psy-publish to validate and persist.
"""


def _run(*args: str) -> subprocess.CompletedProcess:
    """Run a documented command line the way a user would."""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)  # a user has no PYTHONPATH set
    return subprocess.run(
        [sys.executable, *args],
        cwd=PLUGIN_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


class TestPublishCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_documented_invocation_imports_successfully(self):
        report = self.tmp / "draft.md"
        report.write_text(_CLEAN_REPORT, encoding="utf-8")
        r = _run("scripts/publish.py", str(report), "--out", str(self.tmp / "b"))
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_documented_invocation_emits_a_manifest_on_stdout(self):
        report = self.tmp / "draft.md"
        report.write_text(_CLEAN_REPORT, encoding="utf-8")
        r = _run("scripts/publish.py", str(report), "--out", str(self.tmp / "b"))
        manifest = json.loads(r.stdout)
        self.assertEqual(manifest["overall"], "PASS")

    def test_documented_invocation_exits_nonzero_on_block(self):
        # psy-publish.md: a BLOCK manifest means the publish failed.
        report = self.tmp / "draft.md"
        report.write_text("# Report\n\nno required sections, no watermark\n",
                          encoding="utf-8")
        r = _run("scripts/publish.py", str(report), "--out", str(self.tmp / "b"))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(json.loads(r.stdout)["overall"], "BLOCK")


class TestGraphMemoryFragmentCli(unittest.TestCase):
    """Already working; pinned so the plugin root bootstrap is not removed."""

    def test_documented_invocation_imports_successfully(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "fragment.json"
            f.write_text('{"fragments": []}', encoding="utf-8")
            r = _run("scripts/validators/graph_memory_fragment.py", str(f))
            self.assertNotIn("ModuleNotFoundError", r.stderr)


if __name__ == "__main__":
    unittest.main()
