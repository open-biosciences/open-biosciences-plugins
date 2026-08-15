"""Europe PMC adapter. Scope includes PubMed (MED), preprints (PPR),
Bookshelf (NBK) — which is the evidence for the supersede-vs-complement
question in spec section 10.
"""

from __future__ import annotations

from .base import Item, RateLimiter, Response, http_get_json

NAME = "europe-pmc"
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
RATE = 0.5

_SOURCE_TYPE = {"PPR": "preprint", "NBK": "book", "MED": "journal-article"}

_limiter = RateLimiter(RATE)


def _int_or_none(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse(raw: dict) -> Response:
    results = ((raw.get("resultList") or {}).get("result")) or []
    items: list[Item] = []
    for rec in results:
        extra = {
            k: v for k, v in {
                "pmid": rec.get("pmid"),
                "pmcid": rec.get("pmcid"),
            }.items() if v
        }
        journal = ((rec.get("journalInfo") or {}).get("journal")) or {}
        book_details = rec.get("bookOrReportDetails") or {}
        pub_types = (rec.get("pubTypeList") or {}).get("pubType") or []
        items.append(
            Item(
                title=rec.get("title"),
                authors=tuple(
                    a.strip() for a in (rec.get("authorString") or "").split(",") if a.strip()
                ),
                year=_int_or_none(rec.get("pubYear")),
                doi=rec.get("doi"),
                type=_SOURCE_TYPE.get(rec.get("source"), pub_types[0] if pub_types else None),
                venue=journal.get("title") or book_details.get("publisher"),
                publisher=book_details.get("publisher"),
                oa_status="open" if rec.get("isOpenAccess") == "Y" else None,
                extra_ids=extra,
            )
        )
    return Response(total=raw.get("hitCount", len(items)), items=items, raw=raw)


def search(query: str, limit: int = 10) -> Response:
    _limiter.wait()
    return parse(http_get_json(
        BASE, {"query": query, "format": "json", "pageSize": limit, "resultType": "core"}
    ))
