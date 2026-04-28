import tempfile
import unittest
from pathlib import Path

from scripts.sync_expand import expand_file, check_no_markers, INCLUDE_RE


class TestSyncExpand(unittest.TestCase):
    def test_include_re_matches_basic_marker(self):
        m = INCLUDE_RE.search("hello {{include: ../foo.md}} world")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).strip(), "../foo.md")

    def test_expand_file_replaces_marker_with_file_contents(self):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            included = tdp / "included.md"
            included.write_text("INCLUDED CONTENT")
            target = tdp / "target.md"
            target.write_text("before\n{{include: ./included.md}}\nafter")

            expand_file(target)
            result = target.read_text()
            self.assertIn("INCLUDED CONTENT", result)
            self.assertNotIn("{{include:", result)
            self.assertIn("before", result)
            self.assertIn("after", result)

    def test_check_no_markers_passes_clean_tree(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.md").write_text("clean content")
            self.assertEqual(check_no_markers(Path(td)), [])

    def test_check_no_markers_finds_unexpanded(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "a.md"
            f.write_text("oops {{include: ./other.md}}")
            results = check_no_markers(Path(td))
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0], f)


if __name__ == "__main__":
    unittest.main()
