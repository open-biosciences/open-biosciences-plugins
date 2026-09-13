import tempfile
import unittest
from pathlib import Path

from scripts.validators.template_conformance import validate_template_conformance
from scripts.validators import Severity


_WM = (
    "\nSTATUS: UNVALIDATED DRAFT \u2014 citation tiers, evidence labels, and "
    "language filters not yet checked. Run /psy-publish to validate and persist.\n"
)


def _temp_md(text: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                    encoding="utf-8")
    f.write(text)
    f.close()
    return Path(f.name)


_OK = """\
# Report

## Answer
text

## Evidence Packet Summary
text

## Local Context vs External Evidence
text

## Gaps
text

## Sources
- [S1] foo
"""

_MISSING = """\
# Report

## Answer
text

## Sources
- [S1] foo
"""

_OUT_OF_ORDER = """\
# Report

## Sources
- [S1] foo

## Answer
text

## Evidence Packet Summary
text

## Local Context vs External Evidence
text

## Gaps
text
"""


class TestTemplateConformance(unittest.TestCase):
    def test_canonical_passes(self):
        self.assertEqual(
            validate_template_conformance(_temp_md(_OK + _WM)).severity, Severity.PASS,
        )

    def test_missing_section_blocks(self):
        r = validate_template_conformance(_temp_md(_MISSING + _WM))
        self.assertEqual(r.severity, Severity.BLOCK)

    def test_out_of_order_blocks(self):
        r = validate_template_conformance(_temp_md(_OUT_OF_ORDER + _WM))
        self.assertEqual(r.severity, Severity.BLOCK)


if __name__ == "__main__":
    unittest.main()
