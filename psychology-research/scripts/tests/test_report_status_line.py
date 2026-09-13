"""Regression guard for report status lines.

Two bug classes are covered:

1. A retired provenance banner reappearing in a report. The Tier-1a banner
   ("literature MCP not yet wired") was true at 0.1.0 and became false at
   0.3.0 when `psychology-mcp` was declared in `.mcp.json`. It was never
   removed, so reports understated their own provenance for four months.

2. The unvalidated-draft watermark going missing, or drifting away from the
   end of the report where a reader will see it.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.validators import Severity
from scripts.validators.template_conformance import (
    RETIRED_BANNERS,
    WATERMARK_MARKER,
    validate_template_conformance,
)


_SECTIONS = """\
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

_WATERMARK = (
    "STATUS: UNVALIDATED DRAFT — citation tiers, evidence labels, and "
    "language filters not yet checked. Run /psy-publish to validate and persist."
)

_RETIRED_TIER_1A = (
    "PLUGIN VERSION NOTICE: literature MCP not yet wired; claims grounded in "
    "web search and local context only. Citation tiers above SUPPORTED "
    "unavailable for literature claims."
)


def _temp_md(text: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                    encoding="utf-8")
    f.write(text)
    f.close()
    return Path(f.name)


class TestWatermarkFooter(unittest.TestCase):
    def test_canonical_report_with_watermark_passes(self):
        r = validate_template_conformance(_temp_md(_SECTIONS + "\n" + _WATERMARK + "\n"))
        self.assertEqual(r.severity, Severity.PASS, r.findings)

    def test_missing_watermark_blocks(self):
        r = validate_template_conformance(_temp_md(_SECTIONS))
        self.assertEqual(r.severity, Severity.BLOCK)
        self.assertTrue(any("watermark" in f for f in r.findings), r.findings)

    def test_watermark_not_last_blocks(self):
        text = _SECTIONS + "\n" + _WATERMARK + "\n\n## Appendix\ntrailing content\n"
        r = validate_template_conformance(_temp_md(text))
        self.assertEqual(r.severity, Severity.BLOCK)
        self.assertTrue(any("final line" in f for f in r.findings), r.findings)


class TestRetiredBannerGuard(unittest.TestCase):
    def test_retired_tier_1a_banner_blocks(self):
        text = _RETIRED_TIER_1A + "\n\n" + _SECTIONS + "\n" + _WATERMARK + "\n"
        r = validate_template_conformance(_temp_md(text))
        self.assertEqual(r.severity, Severity.BLOCK)
        self.assertTrue(any("retired" in f for f in r.findings), r.findings)

    def test_retired_banner_list_is_not_empty(self):
        # If this list is ever emptied the guard silently stops guarding.
        self.assertTrue(RETIRED_BANNERS)

    def test_watermark_marker_is_exported(self):
        self.assertIn("UNVALIDATED DRAFT", WATERMARK_MARKER)


if __name__ == "__main__":
    unittest.main()
