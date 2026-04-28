"""Sync-time {{include:}} expander and CI marker check.

Usage:
  python3 scripts/sync_expand.py expand <root>   # rewrite files in place
  python3 scripts/sync_expand.py --check <root>  # exit 1 if any unexpanded marker
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

INCLUDE_RE = re.compile(r"\{\{include:\s*([^}]+?)\s*\}\}")

_TEXT_SUFFIXES = {".md", ".markdown", ".txt"}


def expand_file(path: Path) -> bool:
    """Expand markers in path in-place. Returns True if any expansion happened."""
    text = path.read_text(encoding="utf-8")
    changed = False

    def _resolve(match: re.Match[str]) -> str:
        nonlocal changed
        rel = match.group(1).strip()
        included_path = (path.parent / rel).resolve()
        if not included_path.exists():
            raise FileNotFoundError(f"{path}: include target not found: {rel}")
        changed = True
        return included_path.read_text(encoding="utf-8")

    new_text = INCLUDE_RE.sub(_resolve, text)
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return changed


def check_no_markers(root: Path) -> list[Path]:
    """Return list of files under root containing unexpanded markers."""
    offenders: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        if INCLUDE_RE.search(text):
            offenders.append(p)
    return offenders


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=False)
    p_expand = sub.add_parser("expand")
    p_expand.add_argument("root", type=Path)
    parser.add_argument("--check", type=Path, default=None,
                        help="Check root tree; exit 1 if unexpanded markers found")
    args = parser.parse_args()

    if args.check is not None:
        offenders = check_no_markers(args.check)
        if offenders:
            sys.stderr.write("Unexpanded {{include:}} markers found in:\n")
            for o in offenders:
                sys.stderr.write(f"  {o}\n")
            return 1
        return 0

    if args.cmd == "expand":
        for p in args.root.rglob("*"):
            if p.is_file() and p.suffix.lower() in _TEXT_SUFFIXES:
                expand_file(p)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
