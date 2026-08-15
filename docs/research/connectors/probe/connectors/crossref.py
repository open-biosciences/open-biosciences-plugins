"""Crossref adapter. The DOI registry — authoritative for venue class per spec 6.2."""

from __future__ import annotations

import os

from .base import Item, RateLimiter, Response, http_get_json

NAME = "crossref"
BASE = "https://api.crossref.org/works"
RATE = 0.35  # polite pool observed via response headers: x-rate-limit-limit=3,
             # x-rate-limit-interval=1s (~3 req/s); no 429 hit during the 12-cell
             # run at the prior 0.2s value, but this stays under the declared cap
_CONTACT = os.environ.get("PROBE_CONTACT_EMAIL", "").strip()

_limiter = RateLimiter(RATE)


def _first(values) -> str | None:
    if isinstance(values, list) and values:
        return values[0]
    return values or None


def _year(rec: dict) -> int | None:
    parts = ((rec.get("issued") or {}).get("date-parts") or [[]])[0]
    return parts[0] if parts else None


def _retraction(rec: dict) -> str | None:
    for rel in rec.get("update-to") or []:
        if "retract" in str(rel.get("type", "")).lower():
            return "retracted"
    return None


def parse(raw: dict) -> Response:
    message = raw.get("message") or {}
    items: list[Item] = []
    for rec in message.get("items") or []:
        extra = {}
        if rec.get("ISBN"):
            extra["isbn"] = _first(rec["ISBN"])
        if rec.get("ISSN"):
            extra["issn"] = _first(rec["ISSN"])
        items.append(
            Item(
                title=_first(rec.get("title")),
                authors=tuple(
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in (rec.get("author") or [])
                ),
                year=_year(rec),
                doi=rec.get("DOI"),
                type=rec.get("type"),
                venue=_first(rec.get("container-title")),
                publisher=rec.get("publisher"),
                retraction_status=_retraction(rec),
                extra_ids=extra,
            )
        )
    return Response(total=message.get("total-results", len(items)), items=items, raw=raw)


def search(query: str, limit: int = 10) -> Response:
    _limiter.wait()
    params = {"query": query, "rows": limit}
    if _CONTACT:
        params["mailto"] = _CONTACT
    return parse(http_get_json(BASE, params))
