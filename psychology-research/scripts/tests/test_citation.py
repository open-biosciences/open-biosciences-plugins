import unittest
from pathlib import Path

from scripts.validators.citation import validate_citations
from scripts.validators import Severity


FIX = Path(__file__).parent / "fixtures"
TIERS = Path(__file__).parent.parent.parent / "references" / "source-tiers.yaml"


class TestCitationValidator(unittest.TestCase):
    def test_clean_report_passes(self):
        result = validate_citations(FIX / "report_clean_citations.md", TIERS)
        self.assertEqual(result.severity, Severity.PASS)
        self.assertEqual(result.findings, [])

    def test_scribd_source_blocks(self):
        result = validate_citations(FIX / "report_with_scribd.md", TIERS)
        self.assertEqual(result.severity, Severity.BLOCK)
        self.assertTrue(any("scribd" in f.lower() for f in result.findings))


if __name__ == "__main__":
    unittest.main()
