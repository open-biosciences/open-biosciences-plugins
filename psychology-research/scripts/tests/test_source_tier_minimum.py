import unittest
from pathlib import Path

from scripts.validators.source_tier_minimum import validate_source_tier_minimum
from scripts.validators import Severity


TIERS = Path(__file__).parent.parent.parent / "references" / "source-tiers.yaml"


class TestSourceTierMinimum(unittest.TestCase):
    def test_high_stakes_claim_with_tier1_passes(self):
        report = Path(__file__).parent / "fixtures" / "report_high_stakes_tier1.md"
        report.write_text(
            "# Report\n\nEFT is an evidence-based treatment for couples. [S1]\n\n"
            "## Sources\n- [S1] Wiebe & Johnson (2016). https://pubmed.ncbi.nlm.nih.gov/27431257/\n"
        )
        result = validate_source_tier_minimum(report, TIERS)
        self.assertEqual(result.severity, Severity.PASS)

    def test_high_stakes_claim_with_only_tier4_warns(self):
        report = Path(__file__).parent / "fixtures" / "report_high_stakes_tier4.md"
        report.write_text(
            "# Report\n\nThis therapist provides evidence-based treatment. [S1]\n\n"
            "## Sources\n- [S1] Profile, https://www.psychologytoday.com/us/therapists/foo\n"
        )
        result = validate_source_tier_minimum(report, TIERS)
        self.assertEqual(result.severity, Severity.WARN)


if __name__ == "__main__":
    unittest.main()
