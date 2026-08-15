import json
import unittest
from pathlib import Path

from probe.connectors import crossref

FIXTURE = Path(__file__).parent.parent / "fixtures" / "crossref-C1.json"


class TestCrossrefParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(crossref.NAME, "crossref")
        self.assertGreater(crossref.RATE, 0)

    def test_total_comes_from_message_total_results(self):
        resp = crossref.parse(self.raw)
        self.assertEqual(resp.total, self.raw["message"]["total-results"])

    def test_title_is_flattened_from_the_list(self):
        resp = crossref.parse(self.raw)
        self.assertIsInstance(resp.items[0].title, str)

    def test_every_item_carries_a_doi(self):
        """Crossref is the DOI registry; a result without a DOI is a parser bug."""
        resp = crossref.parse(self.raw)
        self.assertTrue(all(i.doi for i in resp.items))

    def test_type_and_publisher_are_captured(self):
        """Spec section 6.2 classifies venue from registered type and publisher."""
        resp = crossref.parse(self.raw)
        self.assertTrue(resp.items[0].type)
        self.assertTrue(resp.items[0].publisher)

    def test_isbn_and_issn_land_in_extra_ids_when_present(self):
        resp = crossref.parse(self.raw)
        for item, rec in zip(resp.items, self.raw["message"]["items"]):
            if rec.get("ISBN"):
                self.assertIn("isbn", item.extra_ids)
            if rec.get("ISSN"):
                self.assertIn("issn", item.extra_ids)

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = crossref.parse({"message": {"total-results": 0, "items": []}})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
