import unittest

from probe.schema import CellRecord, validate


def _rec(**over):
    base = dict(
        connector="crossref",
        query_id="Q1",
        result="hit",
        n_results=12,
        top_result="Some Paper — Author — 2021",
        venue_class="peer-reviewed-article",
        doi_present=True,
        metadata_completeness=("doi", "type", "venue"),
        notes="",
        retrieved_at="2026-08-15T00:00:00Z",
    )
    base.update(over)
    return CellRecord(**base)


class TestValidate(unittest.TestCase):
    def test_valid_record_has_no_problems(self):
        self.assertEqual(validate(_rec()), [])

    def test_rejects_unknown_result(self):
        problems = validate(_rec(result="maybe"))
        self.assertTrue(any("result" in p for p in problems))

    def test_rejects_unknown_venue_class(self):
        problems = validate(_rec(venue_class="journal"))
        self.assertTrue(any("venue_class" in p for p in problems))

    def test_rejects_negative_n_results(self):
        problems = validate(_rec(n_results=-1))
        self.assertTrue(any("n_results" in p for p in problems))

    def test_rejects_unknown_metadata_key(self):
        problems = validate(_rec(metadata_completeness=("doi", "vibes")))
        self.assertTrue(any("vibes" in p for p in problems))

    def test_hit_must_record_top_result(self):
        problems = validate(_rec(top_result=None))
        self.assertTrue(any("top_result" in p for p in problems))

    def test_miss_with_results_requires_a_note(self):
        """Spec section 4: C2 adjacent-match must be explained, not silently scored."""
        problems = validate(_rec(result="miss", n_results=7, top_result=None,
                                 venue_class="unverified", notes=""))
        self.assertTrue(any("note" in p for p in problems))

    def test_miss_with_results_and_a_note_is_valid(self):
        rec = _rec(result="miss", n_results=7, top_result=None,
                   venue_class="unverified", doi_present=False,
                   metadata_completeness=(),
                   notes="token search returned adjacent papers; no construct match")
        self.assertEqual(validate(rec), [])

    def test_clean_miss_is_valid(self):
        rec = _rec(result="miss", n_results=0, top_result=None,
                   venue_class="unverified", doi_present=False,
                   metadata_completeness=(), notes="")
        self.assertEqual(validate(rec), [])

    def test_to_dict_is_json_serialisable(self):
        import json
        json.dumps(_rec().to_dict())
