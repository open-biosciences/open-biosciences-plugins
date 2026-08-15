"""Frozen benchmark queries for psychology-mcp Layer-1 discovery.

FROZEN 2026-08-15 per spec section 4 and ../README.md. Do not edit. The coverage
matrix is citable evidence only while these are pre-registered; adding or rewording
a query invalidates every recorded cell.

Two terms are load-bearing and must not be trimmed:
  Q4 "Frankel" - one of the two named Heroine's Journey authors.
  Q8 "aesthetic engagement" - without it Q8 reduces to self-expansion, the
     adjacent construct already partially grounded on 2026-08-14, so the query
     would measure what already works instead of the gap.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Query:
    id: str
    search: str
    format_axis: str
    subject_axis: str
    role: str  # "coverage" | "positive-control" | "negative-control"


QUERIES: tuple[Query, ...] = (
    Query("Q1", "Internal Family Systems therapy parts Self-leadership protective parts",
          "contemporary-clinical", "clinical-psychotherapy", "coverage"),
    Query("Q2", "Somatic Experiencing Sensorimotor Psychotherapy window of tolerance",
          "contemporary-clinical", "somatic-trauma", "coverage"),
    Query("Q3", "Accelerated Experiential Dynamic Psychotherapy transformance Fosha",
          "contemporary-clinical", "experiential-psychotherapy", "coverage"),
    Query("Q4", "Heroine's Journey Murdock Frankel feminine narrative psychology",
          "monograph-book-canon", "narrative-psychology", "coverage"),
    Query("Q5", "Marston 1928 Emotions of Normal People DISC situational trait",
          "historical-primary", "personality-historical", "coverage"),
    Query("Q6", "secure base safe haven established adult romantic relationships",
          "empirical-journal", "attachment-relational", "coverage"),
    Query("Q7", "Basson responsive sexual desire model spontaneous desire",
          "empirical-journal", "sexology", "coverage"),
    Query("Q8", "shared novel activity aesthetic engagement self-expansion relationship maintenance",
          "empirical-journal", "social-self-expansion", "coverage"),
    Query("Q9", "measurement invariance testing psychological scale validation",
          "empirical-journal", "quantitative-psychometrics", "coverage"),
    Query("Q10", "working memory capacity fluid intelligence",
          "empirical-journal", "experimental-cognitive", "coverage"),
    Query("C1", "emotionally focused therapy couples evidence-based outcome",
          "positive-control", "harness-check", "positive-control"),
    Query("C2", "Neuro-Dynamic Co-Regulation Index Vanderbilt Hayes 2019",
          "negative-control", "hallucination-check", "negative-control"),
)
