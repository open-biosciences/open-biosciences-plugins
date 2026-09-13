"""The bundled report's status footer is derived from the gate result.

A status line typed by a model can drift from reality; a status line computed
at the moment the state is known cannot. `/psy-report` emits the
unvalidated-draft watermark, and `run_gate` replaces it in the bundle copy
with the outcome the gate actually produced.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish import run_gate
from scripts.validators import REGISTRY, Severity, ValidatorResult


_DRAFT = """\
# Report

## Answer
text

## Evidence Packet Summary
text

## Local Context vs External Evidence
text

## Gaps
text

## Sources
- [S1] foo

STATUS: UNVALIDATED DRAFT — citation tiers, evidence labels, and language \
filters not yet checked. Run /psy-publish to validate and persist.
"""


def _result(severity: Severity) -> ValidatorResult:
    return ValidatorResult(name="fake", severity=severity, findings=[])


class TestBundleStatusFooter(unittest.TestCase):
    def setUp(self):
        self._original = list(REGISTRY)
        REGISTRY.clear()
        self._tmp = tempfile.TemporaryDirectory()
        self.draft = Path(self._tmp.name) / "draft.md"
        self.draft.write_text(_DRAFT, encoding="utf-8")

    def tearDown(self):
        REGISTRY.clear()
        REGISTRY.extend(self._original)
        self._tmp.cleanup()

    def _run(self) -> tuple[str, dict]:
        out = Path(self._tmp.name) / "bundle"
        paths = run_gate(report_path=self.draft, out_dir=out)
        return (paths.report.read_text(encoding="utf-8"),
                json.loads(paths.manifest.read_text(encoding="utf-8")))

    def test_draft_watermark_does_not_survive_into_the_bundle(self):
        REGISTRY.append(lambda _p: _result(Severity.PASS))
        report, _ = self._run()
        self.assertNotIn("UNVALIDATED DRAFT", report)

    def test_pass_footer_states_the_gate_passed(self):
        REGISTRY.append(lambda _p: _result(Severity.PASS))
        report, manifest = self._run()
        self.assertEqual(manifest["overall"], "PASS")
        self.assertIn("STATUS: VALIDATED", report)

    def test_warn_footer_states_the_warnings(self):
        REGISTRY.append(lambda _p: _result(Severity.WARN))
        report, manifest = self._run()
        self.assertEqual(manifest["overall"], "WARN")
        self.assertIn("VALIDATED WITH WARNINGS", report)

    def test_block_footer_states_not_for_distribution(self):
        REGISTRY.append(lambda _p: _result(Severity.BLOCK))
        report, manifest = self._run()
        self.assertEqual(manifest["overall"], "BLOCK")
        self.assertIn("BLOCKED", report)
        self.assertIn("not for distribution", report.lower())

    def test_source_draft_on_disk_is_left_untouched(self):
        REGISTRY.append(lambda _p: _result(Severity.PASS))
        self._run()
        self.assertIn("UNVALIDATED DRAFT",
                      self.draft.read_text(encoding="utf-8"))

    def test_report_without_a_watermark_is_not_rewritten(self):
        # Nothing to replace; the gate must not invent a footer.
        self.draft.write_text("# Report\n\nno footer here\n", encoding="utf-8")
        REGISTRY.append(lambda _p: _result(Severity.PASS))
        report, _ = self._run()
        self.assertNotIn("STATUS:", report)


if __name__ == "__main__":
    unittest.main()
