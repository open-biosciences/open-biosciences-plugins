"""Semantic Scholar Academic Graph adapter.

Endpoint verified live 2026-08-15 against
https://api.semanticscholar.org/graph/v1/paper/search — response shape is
{total, offset, next, data[]}, matching the plan's expectation.

Deviation from the plan's draft parser: `openAccessPdf` is present (non-null)
on every observed record, including CLOSED ones with an empty `url` and
`status: "CLOSED"` — so `"open" if rec.get("openAccessPdf") else None` would
mislabel a closed item as open. This parser reads the actual `status` field
instead. `publicationVenue.issn` is also lifted into extra_ids since it is a
Literature Key Registry field (`issn`) that the payload genuinely carries.
"""

from __future__ import annotations

import os
import time
import urllib.error

from .base import Item, RateLimiter, Response, http_get_json

NAME = "semantic-scholar"
BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

# AUTHENTICATED (key issued 2026-08-15). Granted limit is "1 request per second,
# cumulative across all endpoints", with the instruction to "set your rate limit
# to below this threshold to avoid rejected requests" — hence 1.2s, deliberately
# under 1 req/s rather than at it.
#
# Prior UNAUTHENTICATED behaviour, retained because it is the measured finding:
# the shared pool (nominally 1000 req/s across all unauthenticated users) was
# saturated by other traffic across three separate observation windows spanning
# ~1.5 hours. Zero of twelve queries completed. Pacing our own requests further
# apart did not clear it, because the saturation was not ours.
RATE = 1.2

# Key is read from the environment; never hardcoded, never committed.
# .env and .env.* are gitignored in this repo.
_API_KEY = os.environ.get("S2_API_KEY", "").strip()

FIELDS = "title,year,authors,externalIds,venue,publicationTypes,publicationVenue,openAccessPdf"

# Backoff is far shorter than the unauthenticated variant: with a key, a 429
# means we exceeded our own 1/s allocation, which self-corrects in seconds —
# not that a global pool is saturated.
_MAX_RETRIES = 3
_BACKOFF_SECONDS = (3, 8, 20)

_limiter = RateLimiter(RATE)


def parse(raw: dict) -> Response:
    items: list[Item] = []
    for rec in raw.get("data") or []:
        ext = rec.get("externalIds") or {}
        venue_obj = rec.get("publicationVenue") or {}
        types = rec.get("publicationTypes") or []
        oa = rec.get("openAccessPdf") or {}
        oa_status_raw = oa.get("status")
        items.append(
            Item(
                title=rec.get("title"),
                authors=tuple(a.get("name", "") for a in (rec.get("authors") or [])),
                year=rec.get("year"),
                doi=ext.get("DOI"),
                type=types[0] if types else None,
                venue=rec.get("venue") or venue_obj.get("name") or None,
                publisher=venue_obj.get("publisher"),
                oa_status=oa_status_raw.lower() if oa_status_raw else None,
                extra_ids={
                    k: v for k, v in {
                        "semantic_scholar_id": rec.get("paperId"),
                        "pmid": ext.get("PubMed"),
                        "pmcid": ext.get("PubMedCentral"),
                        "arxiv_id": ext.get("ArXiv"),
                        "issn": venue_obj.get("issn"),
                    }.items() if v
                },
            )
        )
    return Response(total=raw.get("total", len(items)), items=items, raw=raw)


def search(query: str, limit: int = 10) -> Response:
    _limiter.wait()
    params = {"query": query, "limit": limit, "fields": FIELDS}
    headers = {"x-api-key": _API_KEY} if _API_KEY else None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            raw = http_get_json(BASE, params, headers=headers)
            return parse(raw)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == _MAX_RETRIES:
                raise
            delay = _BACKOFF_SECONDS[min(attempt, len(_BACKOFF_SECONDS) - 1)]
            time.sleep(delay)
    raise AssertionError("unreachable")  # pragma: no cover
