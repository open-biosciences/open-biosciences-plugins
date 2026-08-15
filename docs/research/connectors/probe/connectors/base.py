"""Shared plumbing for the probe adapters. Stdlib only, deliberately minimal.

This is disposable discovery tooling, not psychology-mcp code. Do not grow it
toward protocol conformance — see the plan's Global Constraints.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

_CONTACT = os.environ.get("PROBE_CONTACT_EMAIL", "").strip()

USER_AGENT = (
    "open-biosciences-connector-probe/1.0 "
    "(+https://github.com/open-biosciences)"
    + (f" mailto:{_CONTACT}" if _CONTACT else "")
)


@dataclass
class Item:
    """One work, normalised just enough to fill a cell record."""

    title: str | None = None
    authors: tuple[str, ...] = ()
    year: int | None = None
    doi: str | None = None
    type: str | None = None
    venue: str | None = None
    publisher: str | None = None
    retraction_status: str | None = None
    oa_status: str | None = None
    extra_ids: dict = field(default_factory=dict)


@dataclass
class Response:
    total: int
    items: list[Item]
    raw: dict


class RateLimiter:
    """Sleep-based minimum interval between calls. Sequential use only."""

    def __init__(self, min_interval: float) -> None:
        self._min = min_interval
        self._last: float | None = None

    def wait(self) -> None:
        if self._last is not None:
            elapsed = time.monotonic() - self._last
            if elapsed < self._min:
                time.sleep(self._min - elapsed)
        self._last = time.monotonic()


def build_url(url: str, params: dict | None = None) -> str:
    if not params:
        return url
    return f"{url}?{urllib.parse.urlencode(params)}"


def build_headers(extra: dict | None = None) -> dict:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if extra:
        headers.update(extra)
    return headers


def http_get_json(url: str, params: dict | None = None,
                  headers: dict | None = None, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(build_url(url, params), headers=build_headers(headers))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))
