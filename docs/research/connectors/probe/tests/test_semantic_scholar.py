import json
import unittest
from pathlib import Path

from probe.connectors import semantic_scholar as s2

FIXTURE = Path(__file__).parent.parent / "fixtures" / "semantic-scholar-C1.json"


class TestSemanticScholarParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(s2.NAME, "semantic-scholar")
        self.assertGreater(s2.RATE, 0)

    def test_parse_returns_a_response(self):
        resp = s2.parse(self.raw)
        self.assertGreaterEqual(resp.total, 0)
        self.assertIsInstance(resp.items, list)
        self.assertIs(resp.raw, self.raw)

    def test_items_carry_a_title(self):
        resp = s2.parse(self.raw)
        self.assertTrue(resp.items, "C1 fixture should contain at least one result")
        self.assertTrue(resp.items[0].title)

    def test_doi_is_lifted_out_of_external_ids(self):
        resp = s2.parse(self.raw)
        dois = [i.doi for i in resp.items if i.doi]
        self.assertTrue(dois, "at least one C1 result should carry a DOI")
        self.assertTrue(all("/" in d for d in dois), "a DOI contains a slash")

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = s2.parse({"total": 0, "data": []})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])


if __name__ == "__main__":
    unittest.main()
