"""PsyArXiv via the OSF Preprints API (JSON:API). Everything from this route
is a preprint by construction, which is why type is set unconditionally.

Search-surface note (see 05-psyarxiv-osf.md section 5 for the full
investigation): OSF's v2 API exposes no ranked-relevance search route for
this repo. `filter[title]` is a real, working filter, but it is a literal
case-insensitive SUBSTRING match against the title field only -- not a
tokenized/boolean word match and not full-text. A top-level `q=` parameter
is silently accepted and silently ignored (confirmed live: identical
results for a nonsense query and no query at all), which is a trap, not a
search route -- it is NOT used here. There is no documented `/v2/search/`
endpoint (confirmed 404 live). filter[title]=query is therefore the best
available mechanism, and it is expected to return few or zero hits for
multi-word natural-language queries, since real titles rarely contain a
five-to-ten word phrase verbatim.
"""

from __future__ import annotations

from .base import Item, RateLimiter, Response, http_get_json

NAME = "psyarxiv-osf"
BASE = "https://api.osf.io/v2/preprints/"
PROVIDER = "psyarxiv"
RATE = 1.0

_limiter = RateLimiter(RATE)


def _year(iso: str | None) -> int | None:
    if not iso or len(iso) < 4:
        return None
    try:
        return int(iso[:4])
    except ValueError:
        return None


def parse(raw: dict) -> Response:
    data = raw.get("data") or []
    items: list[Item] = []
    for rec in data:
        attrs = rec.get("attributes") or {}
        items.append(
            Item(
                title=attrs.get("title"),
                year=_year(attrs.get("date_published")),
                doi=attrs.get("doi"),
                type="preprint",
                venue="PsyArXiv",
                publisher="Center for Open Science",
                oa_status="open",
                extra_ids={"osf_id": rec.get("id")} if rec.get("id") else {},
            )
        )
    total = ((raw.get("links") or {}).get("meta") or {}).get("total", len(items))
    return Response(total=total, items=items, raw=raw)


def search(query: str, limit: int = 10) -> Response:
    _limiter.wait()
    params = {
        "filter[provider]": PROVIDER,
        "filter[title]": query,
        "page[size]": limit,
    }
    return parse(http_get_json(BASE, params))
