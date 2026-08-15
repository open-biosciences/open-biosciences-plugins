import json
import unittest
from pathlib import Path

from probe.connectors import osf

FIXTURE = Path(__file__).parent.parent / "fixtures" / "psyarxiv-osf-C1.json"


class TestOsfParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(osf.NAME, "psyarxiv-osf")
        self.assertGreater(osf.RATE, 0)

    def test_parses_jsonapi_data_array(self):
        resp = osf.parse(self.raw)
        self.assertIsInstance(resp.items, list)
        self.assertIs(resp.raw, self.raw)

    def test_every_item_is_typed_as_a_preprint(self):
        """Everything from this route is a preprint by construction."""
        resp = osf.parse(self.raw)
        self.assertTrue(all(i.type == "preprint" for i in resp.items))

    def test_osf_id_lands_in_extra_ids(self):
        resp = osf.parse(self.raw)
        if resp.items:
            self.assertIn("osf_id", resp.items[0].extra_ids)

    def test_year_is_extracted_from_iso_date_published(self):
        resp = osf.parse(
            {"data": [{"id": "abc", "attributes": {
                "title": "t", "date_published": "2023-04-01T00:00:00.000000Z"}}]}
        )
        self.assertEqual(resp.items[0].year, 2023)

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = osf.parse({"data": []})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])

    def test_parse_extracts_doi_when_present(self):
        """C1's real fixture happens to be an empty result set (substring-only
        search, see 05-psyarxiv-osf.md section 5); exercise DOI extraction
        against a synthetic JSON:API record shaped like an actual hit."""
        resp = osf.parse(
            {"data": [{"id": "xyz12", "attributes": {
                "title": "A Preprint With A DOI",
                "date_published": "2021-06-15T00:00:00.000000Z",
                "doi": "10.31234/osf.io/xyz12"}}],
             "links": {"meta": {"total": 1}}}
        )
        self.assertEqual(resp.total, 1)
        self.assertEqual(resp.items[0].doi, "10.31234/osf.io/xyz12")
        self.assertEqual(resp.items[0].extra_ids["osf_id"], "xyz12")


if __name__ == "__main__":
    unittest.main()
