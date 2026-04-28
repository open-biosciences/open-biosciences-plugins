"""Flat-YAML subset loader for source-tiers.yaml.

The supported subset is one `pattern: tier` per line, plus `## section` headers
and `# comments`. Stdlib-only.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

_LINE_RE = re.compile(r"^\s*([^#:\s][^:]*?)\s*:\s*(\d+)\s*$")


def load_tiers(path: Path) -> dict[str, int]:
    """Parse the flat-YAML source-tiers file. Returns pattern -> tier."""
    result: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _LINE_RE.match(line)
        if m:
            result[m.group(1).strip()] = int(m.group(2))
    return result


def lookup_tier(url: str, tiers: dict[str, int]) -> int | None:
    """Find the tier for a URL by matching its hostname (or hostname+path prefix)
    against the pattern keys. Longer pattern matches win."""
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = urlparse(url).path
    full = host + path

    matches: list[tuple[int, int]] = []  # (pattern_length, tier)
    for pattern, tier in tiers.items():
        if pattern in full or pattern in host:
            matches.append((len(pattern), tier))
    if not matches:
        return None
    matches.sort(reverse=True)
    return matches[0][1]
