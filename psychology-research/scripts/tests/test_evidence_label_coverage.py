import tempfile
import unittest
from pathlib import Path

from scripts.validators.evidence_label_coverage import validate_evidence_label_coverage
from scripts.validators import Severity


def _temp_md(text: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    f.write(text)
    f.close()
    return Path(f.name)


class TestEvidenceLabelCoverage(unittest.TestCase):
    def test_labeled_claim_passes(self):
        path = _temp_md(
            "# Report\n\nAEDP is a modality (SUPPORTED). [S1]\n\n## Sources\n- [S1] foo\n"
        )
        r = validate_evidence_label_coverage(path)
        self.assertEqual(r.severity, Severity.PASS)

    def test_unlabeled_claim_blocks(self):
        path = _temp_md(
            "# Report\n\nAEDP is the gold standard. [S1]\n\n## Sources\n- [S1] foo\n"
        )
        r = validate_evidence_label_coverage(path)
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_unlabeled_claim_in_gaps_section_passes(self):
        path = _temp_md(
            "# Report\n\n## Gaps\n\nUNRESOLVED: no source found for X. [S1]\n\n"
            "## Sources\n- [S1] foo\n"
        )
        r = validate_evidence_label_coverage(path)
        self.assertEqual(r.severity, Severity.PASS)

    def test_local_synthesis_annotation_exempts(self):
        path = _temp_md(
            "# Report\n\nThe overall picture is X (local synthesis). [S1]\n\n"
            "## Sources\n- [S1] foo\n"
        )
        r = validate_evidence_label_coverage(path)
        self.assertEqual(r.severity, Severity.PASS)


if __name__ == "__main__":
    unittest.main()
