import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish import run_gate
from scripts.validators import REGISTRY


FIXTURE = Path(__file__).parent / "fixtures" / "minimal_report.md"


class TestOrchestratorSkeleton(unittest.TestCase):
    def setUp(self):
        # Empty registry for skeleton test.
        self._original = list(REGISTRY)
        REGISTRY.clear()

    def tearDown(self):
        REGISTRY.clear()
        REGISTRY.extend(self._original)

    def test_run_gate_with_no_validators_passes_and_emits_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            paths = run_gate(report_path=FIXTURE, out_dir=out)
            self.assertTrue(paths.report.exists())
            self.assertTrue(paths.evidence_packet.exists())
            self.assertTrue(paths.manifest.exists())
            self.assertTrue(paths.content_hash.exists())

    def test_manifest_records_zero_validator_results_when_registry_empty(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            paths = run_gate(report_path=FIXTURE, out_dir=out)
            data = json.loads(paths.manifest.read_text())
            self.assertEqual(data["validators"], [])
            self.assertEqual(data["overall"], "PASS")

    def test_run_gate_blocks_on_block_severity(self):
        def fail_validator(_: Path):
            from scripts.validators import ValidatorResult, Severity
            return ValidatorResult(
                name="fake",
                severity=Severity.BLOCK,
                findings=["intentional"],
            )

        REGISTRY.append(fail_validator)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            paths = run_gate(report_path=FIXTURE, out_dir=out)
            data = json.loads(paths.manifest.read_text())
            self.assertEqual(data["overall"], "BLOCK")


if __name__ == "__main__":
    unittest.main()
