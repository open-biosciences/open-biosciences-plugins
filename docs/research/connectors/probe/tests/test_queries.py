import unittest

from probe.queries import QUERIES, Query


class TestQueries(unittest.TestCase):
    def test_twelve_queries_frozen(self):
        self.assertEqual(len(QUERIES), 12)

    def test_ids_are_q1_through_q10_plus_two_controls(self):
        ids = [q.id for q in QUERIES]
        self.assertEqual(ids, [f"Q{n}" for n in range(1, 11)] + ["C1", "C2"])

    def test_exactly_one_positive_and_one_negative_control(self):
        roles = [q.role for q in QUERIES]
        self.assertEqual(roles.count("positive-control"), 1)
        self.assertEqual(roles.count("negative-control"), 1)
        self.assertEqual(roles.count("coverage"), 10)

    def test_every_query_carries_both_axes(self):
        for q in QUERIES:
            self.assertTrue(q.format_axis, f"{q.id} missing format_axis")
            self.assertTrue(q.subject_axis, f"{q.id} missing subject_axis")

    def test_queries_are_immutable(self):
        with self.assertRaises(Exception):
            QUERIES[0].search = "tampered"

    def test_subject_axes_are_distinct_across_coverage_queries(self):
        axes = [q.subject_axis for q in QUERIES if q.role == "coverage"]
        self.assertEqual(len(axes), len(set(axes)), "coverage queries must not duplicate a subject axis")
