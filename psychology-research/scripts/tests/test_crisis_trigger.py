import tempfile
import unittest
from pathlib import Path

from scripts.validators.crisis_trigger import validate_crisis_trigger
from scripts.validators import Severity


CRISIS_REF = (
    Path(__file__).parent.parent.parent / "references" / "crisis-resources.md"
)


class TestCrisisTrigger(unittest.TestCase):
    def test_no_crisis_keywords_passes(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Discussion of routine therapy modalities.")
            f.flush()
            r = validate_crisis_trigger(Path(f.name), CRISIS_REF)
            self.assertEqual(r.severity, Severity.PASS)

    def test_crisis_keyword_without_preamble_blocks(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("The user mentioned suicidal ideation. Discussion follows.")
            f.flush()
            r = validate_crisis_trigger(Path(f.name), CRISIS_REF)
            self.assertEqual(r.severity, Severity.BLOCK)

    def test_crisis_keyword_with_preamble_passes(self):
        preamble = CRISIS_REF.read_text(encoding="utf-8")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(preamble)
            f.write("\n\nDiscussion mentions suicidal ideation in context.\n")
            f.flush()
            r = validate_crisis_trigger(Path(f.name), CRISIS_REF)
            self.assertEqual(r.severity, Severity.PASS)


if __name__ == "__main__":
    unittest.main()
