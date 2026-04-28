import unittest
from pathlib import Path
import tempfile

from scripts.source_tiers_loader import load_tiers, lookup_tier


class TestSourceTiersLoader(unittest.TestCase):
    def _write(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        f.write(content)
        f.close()
        return Path(f.name)

    def test_parses_flat_pattern_to_tier(self):
        path = self._write("pubmed.ncbi.nlm.nih.gov: 1\npsychologytoday.com: 4\n")
        tiers = load_tiers(path)
        self.assertEqual(tiers["pubmed.ncbi.nlm.nih.gov"], 1)
        self.assertEqual(tiers["psychologytoday.com"], 4)

    def test_skips_section_headers_and_comments(self):
        content = "## Tier 1\n# a comment\npubmed.ncbi.nlm.nih.gov: 1\n"
        path = self._write(content)
        tiers = load_tiers(path)
        self.assertEqual(tiers, {"pubmed.ncbi.nlm.nih.gov": 1})

    def test_lookup_tier_matches_subdomain(self):
        tiers = {"pubmed.ncbi.nlm.nih.gov": 1, "scribd.com": 6}
        self.assertEqual(lookup_tier("https://pubmed.ncbi.nlm.nih.gov/12345/", tiers), 1)
        self.assertEqual(lookup_tier("https://www.scribd.com/document/abc", tiers), 6)

    def test_lookup_tier_unknown_url_returns_none(self):
        tiers = {"pubmed.ncbi.nlm.nih.gov": 1}
        self.assertIsNone(lookup_tier("https://random.example.com/", tiers))


if __name__ == "__main__":
    unittest.main()
