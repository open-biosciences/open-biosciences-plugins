"""OpenAlex adapter. Keyless; the polite pool wants a mailto."""

from __future__ import annotations

import os

from .base import Item, RateLimiter, Response, http_get_json

NAME = "openalex"
BASE = "https://api.openalex.org/works"
RATE = 0.15  # polite pool allows ~10/sec; stay well under
_CONTACT = os.environ.get("PROBE_CONTACT_EMAIL", "").strip()

_limiter = RateLimiter(RATE)


def _bare_doi(value: str | None) -> str | None:
    if not value:
        return None
    return value.rsplit("doi.org/", 1)[-1]


def parse(raw: dict) -> Response:
    items: list[Item] = []
    for rec in raw.get("results") or []:
        source = ((rec.get("primary_location") or {}).get("source")) or {}
        oa = rec.get("open_access") or {}
        retracted = rec.get("is_retracted")
        items.append(
            Item(
                title=rec.get("display_name") or rec.get("title"),
                authors=tuple(
                    (a.get("author") or {}).get("display_name", "")
                    for a in (rec.get("authorships") or [])
                ),
                year=rec.get("publication_year"),
                doi=_bare_doi(rec.get("doi")),
                type=rec.get("type"),
                venue=source.get("display_name"),
                publisher=source.get("host_organization_name"),
                retraction_status=None if retracted is None
                else ("retracted" if retracted else "not-retracted"),
                oa_status=oa.get("oa_status"),
                extra_ids={"openalex_id": rec.get("id")} if rec.get("id") else {},
            )
        )
    return Response(total=(raw.get("meta") or {}).get("count", len(items)), items=items, raw=raw)


def search(query: str, limit: int = 10) -> Response:
    _limiter.wait()
    params = {"search": query, "per-page": limit}
    if _CONTACT:
        params["mailto"] = _CONTACT
    return parse(http_get_json(BASE, params))
