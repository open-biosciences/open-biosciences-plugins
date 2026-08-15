"""The cell-record contract. One record per (connector, query) pair; 60 total."""

from __future__ import annotations

from dataclasses import asdict, dataclass

RESULTS = ("hit", "partial", "miss")

VENUE_CLASSES = (
    "peer-reviewed-article",
    "book",
    "book-chapter",
    "institute-publication",
    "preprint",
    "guideline",
    "grey",
    "commentary",
    "unverified",
)

# Literature Key Registry — spec section 6.3
REGISTRY_KEYS = (
    "doi", "pmid", "pmcid", "openalex_id",
    "semantic_scholar_id", "osf_id", "arxiv_id", "isbn", "issn",
)

# Envelope fields the venue classifier needs — spec section 6.2
ENVELOPE_FIELDS = ("type", "venue", "publisher", "retraction_status", "oa_status")

_ALLOWED_METADATA = frozenset(REGISTRY_KEYS) | frozenset(ENVELOPE_FIELDS)


@dataclass
class CellRecord:
    connector: str
    query_id: str
    result: str
    n_results: int
    top_result: str | None
    venue_class: str
    doi_present: bool
    metadata_completeness: tuple[str, ...]
    notes: str
    retrieved_at: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["metadata_completeness"] = list(self.metadata_completeness)
        return d


def validate(rec: CellRecord) -> list[str]:
    """Return a list of problems. Empty list means the record is well-formed."""
    problems: list[str] = []

    if rec.result not in RESULTS:
        problems.append(f"result {rec.result!r} not one of {RESULTS}")
    if rec.venue_class not in VENUE_CLASSES:
        problems.append(f"venue_class {rec.venue_class!r} not one of {VENUE_CLASSES}")
    if rec.n_results < 0:
        problems.append("n_results must be >= 0")

    for key in rec.metadata_completeness:
        if key not in _ALLOWED_METADATA:
            problems.append(f"metadata_completeness key {key!r} is not a registry or envelope field")

    if rec.result != "miss" and not rec.top_result:
        problems.append("a hit or partial must record top_result")

    if rec.result == "miss" and rec.n_results > 0 and not rec.notes:
        problems.append(
            "a miss with n_results > 0 must carry a note explaining the adjacent match "
            "(spec section 4, C2 scoring)"
        )

    return problems
