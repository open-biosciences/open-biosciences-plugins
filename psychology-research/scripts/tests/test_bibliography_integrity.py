import tempfile
import unittest
from pathlib import Path

from scripts.validators.bibliography_integrity import validate_bibliography_integrity
from scripts.validators import Severity


def _temp_md(text: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    f.write(text)
    f.close()
    return Path(f.name)


class TestBibliographyIntegrity(unittest.TestCase):
    def test_balanced_passes(self):
        path = _temp_md("Body. [S1]\n\n## Sources\n- [S1] foo\n")
        self.assertEqual(
            validate_bibliography_integrity(path).severity, Severity.PASS,
        )

    def test_orphan_marker_blocks(self):
        path = _temp_md("Body. [S2]\n\n## Sources\n- [S1] foo\n")
        r = validate_bibliography_integrity(path)
        self.assertEqual(r.severity, Severity.BLOCK)
        self.assertTrue(any("S2" in f for f in r.findings))

    def test_unreferenced_entry_blocks(self):
        path = _temp_md("Body. [S1]\n\n## Sources\n- [S1] foo\n- [S99] unused\n")
        r = validate_bibliography_integrity(path)
        self.assertEqual(r.severity, Severity.BLOCK)
        self.assertTrue(any("S99" in f for f in r.findings))


if __name__ == "__main__":
    unittest.main()
