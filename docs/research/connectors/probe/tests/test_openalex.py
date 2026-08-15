import json
import unittest
from pathlib import Path

from probe.connectors import openalex

FIXTURE = Path(__file__).parent.parent / "fixtures" / "openalex-C1.json"


class TestOpenAlexParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(openalex.NAME, "openalex")
        self.assertGreater(openalex.RATE, 0)

    def test_total_comes_from_meta_count(self):
        resp = openalex.parse(self.raw)
        self.assertEqual(resp.total, self.raw["meta"]["count"])

    def test_doi_is_bare_not_a_url(self):
        """OpenAlex returns https://doi.org/10.x; a DOI field should hold 10.x."""
        resp = openalex.parse(self.raw)
        dois = [i.doi for i in resp.items if i.doi]
        self.assertTrue(dois)
        self.assertTrue(all(d.startswith("10.") for d in dois))

    def test_type_is_captured_for_venue_classification(self):
        resp = openalex.parse(self.raw)
        self.assertTrue(any(i.type for i in resp.items))

    def test_retraction_status_is_captured_when_present(self):
        resp = openalex.parse(self.raw)
        if "is_retracted" in (self.raw["results"][0] if self.raw["results"] else {}):
            self.assertIn(resp.items[0].retraction_status, ("retracted", "not-retracted"))

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = openalex.parse({"meta": {"count": 0}, "results": []})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
