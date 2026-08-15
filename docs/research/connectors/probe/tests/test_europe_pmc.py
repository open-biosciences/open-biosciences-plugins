import json
import unittest
from pathlib import Path

from probe.connectors import europe_pmc

FIXTURE = Path(__file__).parent.parent / "fixtures" / "europe-pmc-C1.json"


class TestEuropePmcParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(europe_pmc.NAME, "europe-pmc")
        self.assertGreater(europe_pmc.RATE, 0)

    def test_total_comes_from_hit_count(self):
        resp = europe_pmc.parse(self.raw)
        self.assertEqual(resp.total, self.raw["hitCount"])

    def test_pmid_and_pmcid_land_in_extra_ids(self):
        resp = europe_pmc.parse(self.raw)
        ids = [i.extra_ids for i in resp.items]
        self.assertTrue(any("pmid" in d for d in ids))

    def test_author_string_is_split_into_a_tuple(self):
        resp = europe_pmc.parse(self.raw)
        self.assertIsInstance(resp.items[0].authors, tuple)

    def test_year_is_an_int(self):
        resp = europe_pmc.parse(self.raw)
        years = [i.year for i in resp.items if i.year is not None]
        self.assertTrue(all(isinstance(y, int) for y in years))

    def test_preprint_source_maps_to_preprint_type(self):
        """source=PPR is Europe PMC's preprint marker; it must survive parsing."""
        resp = europe_pmc.parse(
            {"hitCount": 1, "resultList": {"result": [
                {"id": "PPR1", "source": "PPR", "title": "t", "pubYear": "2024"}]}}
        )
        self.assertEqual(resp.items[0].type, "preprint")

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = europe_pmc.parse({"hitCount": 0, "resultList": {"result": []}})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
