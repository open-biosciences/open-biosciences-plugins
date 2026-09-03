import tempfile
import unittest
from pathlib import Path

from scripts.validators.no_citations_found import validate_no_citations_found
from scripts.validators import Severity


def _tmp(body: str) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(body)
        return Path(f.name)


class TestNoCitationsFound(unittest.TestCase):
    def test_report_with_markers_passes(self):
        r = validate_no_citations_found(_tmp("AEDP is SUPPORTED. [S1]\n\n## Sources\n- [S1] x — y — https://z"))
        self.assertEqual(r.severity, Severity.PASS)

    def test_report_with_no_sources_at_all_warns(self):
        r = validate_no_citations_found(_tmp("Some prose with no sources."))
        self.assertEqual(r.severity, Severity.WARN)
        self.assertEqual(len(r.findings), 1)

    def test_claim_table_shape_warns_with_hint(self):
        body = "| C1 | claim | SUPPORTED | [Dodson 2016](https://chadd.org/x.pdf) |"
        r = validate_no_citations_found(_tmp(body))
        self.assertEqual(r.severity, Severity.WARN)
        self.assertEqual(len(r.findings), 2)
        self.assertIn("shape the gate does not recognise", r.findings[1])


if __name__ == "__main__":
    unittest.main()
