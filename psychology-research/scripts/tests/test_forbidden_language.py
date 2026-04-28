import tempfile
import unittest
from pathlib import Path

from scripts.validators.forbidden_language import (
    load_wordlist, validate_forbidden_language,
)
from scripts.validators import Severity


WORDLIST = Path(__file__).parent.parent.parent / "references" / "forbidden-language.md"


class TestForbiddenLanguage(unittest.TestCase):
    def test_load_wordlist_extracts_bullet_terms(self):
        terms = load_wordlist(WORDLIST)
        self.assertIn("premier", terms)
        self.assertIn("gold standard", terms)

    def test_clean_text_passes(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("This is a competent therapist who has training in IFS.")
            f.flush()
            result = validate_forbidden_language(Path(f.name), WORDLIST)
            self.assertEqual(result.severity, Severity.PASS)

    def test_text_with_premier_warns(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("This is a premier clinician.")
            f.flush()
            result = validate_forbidden_language(Path(f.name), WORDLIST)
            self.assertEqual(result.severity, Severity.WARN)
            self.assertTrue(any("premier" in f.lower() for f in result.findings))


if __name__ == "__main__":
    unittest.main()
