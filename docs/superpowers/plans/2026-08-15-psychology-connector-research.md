# psychology-mcp Layer-1 Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Tasks 3–7 are dispatched in parallel, one agent per connector** — see "Fan-out protocol" below. Tasks 1, 2, and 8–10 run inline.

**Goal:** Produce the Layer-1 discovery evidence — five connector dossiers, a 60-cell coverage matrix, a literature envelope contract, and a decision document — that a `psychology-mcp` Layer-2 build will be specified from.

**Architecture:** A disposable stdlib probe harness under `docs/research/connectors/probe/` runs 12 pre-registered queries against 5 scholarly APIs, emitting validated cell records. Each API gets one dossier written from its own probe results plus a documentation read. The aggregated metadata findings then drive the literature envelope design, and the whole thing terminates in `DECISION.md`.

**Tech Stack:** Python 3.10+ stdlib only (`urllib.request`, `json`, `dataclasses`) · `unittest.TestCase` run under pytest · Markdown deliverables.

**Spec:** [`docs/superpowers/specs/2026-08-15-psychology-connector-research-design.md`](../specs/2026-08-15-psychology-connector-research-design.md)

## Global Constraints

Every task's requirements implicitly include these. Values copied verbatim from the spec.

- **Working directory:** `/home/donbr/open-biosciences/open-biosciences-plugins-connector-research`, branch `feat/psychology-connector-research`. This repo is cloned into three roots ([AGE-567]). **`/home/donbr/open-biosciences/` is the authoritative root** — it is the one `open-biosciences.code-workspace` defines. Do not author into `/home/donbr/hci/open-biosciences-plugins` or `/mnt/c/Users/donbr/codex/open-biosciences-plugins`.
- **"No file outside `docs/research/connectors/` is created or modified"** (spec §11), excepting this plan and the spec itself.
- **The probe harness is disposable discovery tooling, not `psychology-mcp` code.** Building `psychology-mcp` is an explicit non-goal (spec §3.2, §9). Do not add abstractions, packaging, or protocol conformance to the harness in anticipation of Layer 2. It exists to fill 60 cells reproducibly and then to be read, not shipped.
- **Stdlib only.** Not from an invented repo rule — this is a plugin repo with no Python dependency file, and adding one for throwaway tooling would be wrong. Five simple GET+JSON clients do not need `httpx`.
- **Tests use `unittest.TestCase`**, matching `psychology-research/scripts/tests/`. No `conftest.py`, no `pytest.ini`.
- **Run tests from `docs/research/connectors/`:** `python3 -m pytest probe/tests -v`
- **The 12 queries are frozen after Task 1.** Editing or rewording one invalidates every recorded cell. The benchmark is only citable evidence while pre-registered.
- **Sequential probing, never parallel.** Respect each API's rate limit; spec §10 names throttling as a risk.
- **`DECISION.md` proposes deltas; it applies none.**
- **Commit trailer on every commit:** `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`

## Fan-out protocol

Tasks 3–7 are five independent units — each touches only its own adapter, test, fixture, results file, and dossier — and are dispatched **in parallel, one agent per connector**, per ADR-005 ("Git Worktrees for Parallel MCP Server Development", Accepted). Tasks 1, 2 and 8–10 are gates or need all five complete, and run inline.

**Phase 0 applied.** ADR-005's prerequisite is a namespace refactor so no two agents write the same file. Here there is exactly one shared write — the connector registry in `run.py` — and Task 2 removes it by declaring all five entries up front as a static name→module map with lazy import. **Tasks 3–7 therefore never touch `run.py`.** The five agents share `base.py`, `schema.py`, `queries.py` and `run.py` as **read-only**.

**Verification is by artefact, never by report.** A subagent can report a twelve-call loop complete without having run it ([[feedback-verify-subagent-tool-loop-completion]] — a 43-call loop was reported "0 errors" with the calls never made). Do not accept a connector as done on its agent's say-so. The controller verifies, from the main loop:

```bash
cd docs/research/connectors
python3 - <<'PY'
import json, sys
from pathlib import Path
from probe.schema import CellRecord, validate
ok = True
for name in ["semantic-scholar","openalex","crossref","europe-pmc","psyarxiv-osf"]:
    fx = Path(f"probe/fixtures/{name}-C1.json")
    rs = Path(f"probe/results/{name}.json")
    if not fx.exists() or fx.stat().st_size < 200:
        print(f"{name}: FIXTURE MISSING OR STUB"); ok = False; continue
    json.loads(fx.read_text())                       # must be real JSON from the API
    rows = json.loads(rs.read_text())
    if len(rows) != 12:
        print(f"{name}: {len(rows)} cells, expected 12"); ok = False; continue
    for r in rows:
        r["metadata_completeness"] = tuple(r["metadata_completeness"])
        for p in validate(CellRecord(**r)):
            print(f"{name} {r['query_id']}: {p}"); ok = False
    print(f"{name}: OK")
sys.exit(0 if ok else 1)
PY
```

A fabricated run cannot produce a real API payload in `fixtures/` or twelve records that pass `validate()`. That is the gate.

**Model.** Use sonnet or better for these agents — never haiku. The cited failure was a haiku subagent on a monotonous sequential loop, which is exactly the shape of a twelve-cell probe.

**Consistency.** Five agents classifying `venue_class` independently will diverge, and Task 8's matrix compares them. Task 2 therefore writes a **classification rubric** that all five agents receive verbatim; deviation from it is a review finding.

**Rate limits.** Five agents against five *different* APIs share no limit (ADR-005 Risk 2 concerns concurrent hits on the *same* API). Each adapter carries its own `RateLimiter`; agents must not raise another connector's `RATE`.

## File Structure

```
docs/research/connectors/
├── README.md                     Method, frozen queries, cell schema, re-run instructions
├── 00-coverage-matrix.md         60 cells aggregated
├── 01-semantic-scholar.md        \
├── 02-openalex.md                 |
├── 03-crossref.md                 |  Dossiers — spec §5 template, §1–§8
├── 04-europe-pmc.md               |
├── 05-psyarxiv-osf.md            /
├── 06-literature-envelope.md     Layer-2 response contract
├── DECISION.md                   Roster, AGE-548 q3, interim delta, limitations
└── probe/
    ├── queries.py                Frozen Query tuple — one responsibility: the benchmark
    ├── schema.py                 CellRecord + validate() — one responsibility: the record contract
    ├── run.py                    CLI: run one connector's 12 cells, write results JSON
    ├── connectors/
    │   ├── base.py               Item, Response, RateLimiter, build_url, http_get_json
    │   ├── semantic_scholar.py   NAME, RATE, search(), parse()
    │   ├── openalex.py
    │   ├── crossref.py
    │   ├── europe_pmc.py
    │   └── osf.py
    ├── fixtures/<connector>-<query_id>.json    Raw responses used by parser tests
    ├── results/<connector>.json                12 validated cell records
    └── tests/
        ├── test_queries.py
        ├── test_schema.py
        ├── test_base.py
        └── test_<connector>.py   One per adapter — parses its recorded fixture
```

Each adapter splits `search()` (network) from `parse()` (pure). Only `parse()` is unit-tested, against a fixture recorded from the live API. You cannot pre-write a parser for a response shape you have not observed — so each API task records the fixture first, then tests against it.

---

### Task 1: Freeze the benchmark

**Files:**
- Create: `docs/research/connectors/README.md`

**Interfaces:**
- Consumes: nothing
- Produces: the frozen query list that `probe/queries.py` (Task 2) transcribes, and the cell-record field list that `probe/schema.py` (Task 2) implements

- [ ] **Step 1: Create the deliverable directory**

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research
mkdir -p docs/research/connectors/probe/connectors docs/research/connectors/probe/tests \
         docs/research/connectors/probe/fixtures docs/research/connectors/probe/results
```

- [ ] **Step 2: Write `docs/research/connectors/README.md`**

Content — the 12 queries verbatim from spec §4, the cell schema from spec §4.1, the provenance note, and re-run instructions:

````markdown
# Connector discovery — method and frozen benchmark

Layer-1 discovery for `psychology-mcp`. Spec:
[`../../superpowers/specs/2026-08-15-psychology-connector-research-design.md`](../../superpowers/specs/2026-08-15-psychology-connector-research-design.md)

## Provenance of the benchmark — read before changing anything

These 12 queries were **frozen on 2026-08-15, before any candidate API was contacted.**
That is what makes the coverage matrix citable evidence rather than connector shopping.

- **Q1–Q6** are the six `UNRESOLVED` results recorded by an independent run on
  2026-08-14 (`hci-canon` `research/vibrancy-runs/2026-08-14-don-lila/literature-grounding.md`),
  written down before any connector was under consideration.
- **Q7–Q8** extend that to one query per modality in the consuming framework.
- **Q9–Q10** were added during spec design to close a subject-axis blind spot: Q1–Q8
  are entirely clinical and social, and quantitative-methods and experimental-cognitive
  literature sit in a different publisher ecosystem.
- **C1–C2** are controls, not coverage.

**Editing or rewording any query invalidates every recorded cell.** If a query must
change, the matrix is re-run from scratch and this note records why.

## The benchmark

| # | Query | Format axis | Subject axis |
|---|---|---|---|
| Q1 | Internal Family Systems therapy parts Self-leadership protective parts | contemporary-clinical | clinical-psychotherapy |
| Q2 | Somatic Experiencing Sensorimotor Psychotherapy window of tolerance | contemporary-clinical | somatic-trauma |
| Q3 | Accelerated Experiential Dynamic Psychotherapy transformance Fosha | contemporary-clinical | experiential-psychotherapy |
| Q4 | Heroine's Journey Murdock feminine narrative psychology | monograph-book-canon | narrative-psychology |
| Q5 | Marston 1928 Emotions of Normal People DISC situational trait | historical-primary | personality-historical |
| Q6 | secure base safe haven established adult romantic relationships | empirical-journal | attachment-relational |
| Q7 | Basson responsive sexual desire model spontaneous desire | empirical-journal | sexology |
| Q8 | shared novel activity self-expansion relationship maintenance | empirical-journal | social-self-expansion |
| Q9 | measurement invariance testing psychological scale validation | empirical-journal | quantitative-psychometrics |
| Q10 | working memory capacity fluid intelligence | empirical-journal | experimental-cognitive |
| C1 | emotionally focused therapy couples evidence-based outcome | *positive control* | *harness check* |
| C2 | Neuro-Dynamic Co-Regulation Index Vanderbilt Hayes 2019 | *negative control* | *hallucination check* |

**Q6** is deliberately scoped to *established* dyads: PubMed returned only
fledgling-relationship literature, and the query preserves that discrimination.

**C1 is scored separately** and is not counted toward any connector's coverage score.
A connector that misses it has a broken client, not a coverage gap.

**C2 scoring — "zero results" is the wrong bar.** Token-relevance engines return
topically adjacent work by matching individual words (`co-regulation`, `index`) even
when the construct does not exist. That is normal retrieval.

| Outcome | Score | Record |
|---|---|---|
| Zero results | pass | `result: miss`, `n_results: 0` |
| Non-empty, no construct match | pass | `result: miss`, `n_results: N`, note `"token search returned adjacent papers; no construct match"` |
| A result presented as matching the fabricated construct or citation | **fail** | Finding in that dossier's §7 |

The failure mode under test is a confident exact match for something that does not exist.

## Cell record schema

| Field | Values |
|---|---|
| `connector` | connector name |
| `query_id` | `Q1`–`Q10`, `C1`, `C2` |
| `result` | `hit` / `partial` / `miss` |
| `n_results` | integer ≥ 0 |
| `top_result` | title, authors, year |
| `venue_class` | `peer-reviewed-article` `book` `book-chapter` `institute-publication` `preprint` `guideline` `grey` `commentary` `unverified` |
| `doi_present` | boolean |
| `metadata_completeness` | registry keys and envelope fields the API actually returned |
| `notes` | free text |
| `retrieved_at` | ISO-8601 UTC |

`metadata_completeness` is load-bearing: a connector returning results but no venue
type cannot support the literature envelope, which is a selection criterion
independent of coverage.

## Re-running

```bash
cd docs/research/connectors
export PROBE_CONTACT_EMAIL="you@example.com"   # Crossref/OpenAlex polite pool
python3 -m probe.run --connector semantic-scholar      # writes probe/results/semantic-scholar.json
python3 -m pytest probe/tests -v
```

Probes run **sequentially, one connector at a time**, respecting each API's rate limit.

Raw responses are recorded to `probe/fixtures/` for C1 and one representative coverage
query per connector — enough to unit-test each parser without storing 60 full payloads.
The 12 validated cell records per connector live in `probe/results/`.
````

- [ ] **Step 3: Verify the queries match the spec exactly**

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research
grep -c "^| Q[0-9]" docs/research/connectors/README.md    # expect 10
grep -c "^| C[12]" docs/research/connectors/README.md     # expect 2
```

Expected: `10` then `2`. Then read spec §4's table beside the README's and confirm each query's format and subject axis matches.

- [ ] **Step 4: Commit**

```bash
git add docs/research/connectors/README.md
git commit -m "docs(connectors): freeze the 12-query discovery benchmark

Pre-registers the benchmark before any candidate API is contacted, which
is what makes the coverage matrix citable rather than shopped. Q1-Q6 come
from an independent 2026-08-14 run's UNRESOLVED list; Q7-Q8 extend to one
query per modality; Q9-Q10 close the subject-axis blind spot; C1/C2 are
controls.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 5: STOP — maintainer approval gate**

Spec §8 step 1: *"Maintainer approves before any API is contacted."*

Report the frozen benchmark to the maintainer and **stop**. Do not begin Task 2. Do not contact any API. A benchmark approved after results are seen is not pre-registered, and the entire evidentiary value of the matrix depends on this gate being real.

---

### Task 2: Probe harness core

**Files:**
- Create: `docs/research/connectors/probe/__init__.py`, `probe/queries.py`, `probe/schema.py`, `probe/connectors/__init__.py`, `probe/connectors/base.py`, `probe/run.py`, `probe/RUBRIC.md`, `probe/tests/__init__.py`
- Test: `probe/tests/test_queries.py`, `probe/tests/test_schema.py`, `probe/tests/test_base.py`

**This task must complete before any of Tasks 3–7 are dispatched.** It produces everything the five parallel agents share, including the pre-declared registry that removes their only shared write.

**Interfaces:**
- Consumes: the frozen queries and cell schema from Task 1's `README.md`
- Produces:
  - `queries.QUERIES: tuple[Query, ...]` where `Query(id, search, format_axis, subject_axis, role)`
  - `schema.CellRecord(connector, query_id, result, n_results, top_result, venue_class, doi_present, metadata_completeness, notes, retrieved_at)` and `schema.validate(rec) -> list[str]`
  - `connectors.base.Item`, `connectors.base.Response(total, items, raw)`, `connectors.base.RateLimiter(min_interval).wait()`, `connectors.base.build_url(url, params) -> str`, `connectors.base.build_headers(extra) -> dict`, `connectors.base.http_get_json(url, params, headers, timeout) -> dict`
  - `run.CONNECTORS: dict[str, str]` — all five connector names pre-declared, mapped to module names; `run.run_connector(name) -> list[CellRecord]`
  - `probe/RUBRIC.md` — the venue-class and metadata-completeness classification rubric, passed verbatim to every Task 3–7 agent

- [ ] **Step 1: Write the failing tests for `queries.py`**

`probe/tests/test_queries.py`:

```python
import unittest

from probe.queries import QUERIES, Query


class TestQueries(unittest.TestCase):
    def test_twelve_queries_frozen(self):
        self.assertEqual(len(QUERIES), 12)

    def test_ids_are_q1_through_q10_plus_two_controls(self):
        ids = [q.id for q in QUERIES]
        self.assertEqual(ids, [f"Q{n}" for n in range(1, 11)] + ["C1", "C2"])

    def test_exactly_one_positive_and_one_negative_control(self):
        roles = [q.role for q in QUERIES]
        self.assertEqual(roles.count("positive-control"), 1)
        self.assertEqual(roles.count("negative-control"), 1)
        self.assertEqual(roles.count("coverage"), 10)

    def test_every_query_carries_both_axes(self):
        for q in QUERIES:
            self.assertTrue(q.format_axis, f"{q.id} missing format_axis")
            self.assertTrue(q.subject_axis, f"{q.id} missing subject_axis")

    def test_queries_are_immutable(self):
        with self.assertRaises(Exception):
            QUERIES[0].search = "tampered"

    def test_subject_axes_are_distinct_across_coverage_queries(self):
        axes = [q.subject_axis for q in QUERIES if q.role == "coverage"]
        self.assertEqual(len(axes), len(set(axes)), "coverage queries must not duplicate a subject axis")
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_queries.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'probe'`

- [ ] **Step 3: Implement `probe/queries.py`**

Also create empty `probe/__init__.py`, `probe/connectors/__init__.py`, `probe/tests/__init__.py`.

```python
"""Frozen benchmark queries for psychology-mcp Layer-1 discovery.

FROZEN 2026-08-15 per spec section 4. Do not edit. The coverage matrix is
citable evidence only while these are pre-registered; adding or rewording a
query invalidates every recorded cell.
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
    Query("Q4", "Heroine's Journey Murdock feminine narrative psychology",
          "monograph-book-canon", "narrative-psychology", "coverage"),
    Query("Q5", "Marston 1928 Emotions of Normal People DISC situational trait",
          "historical-primary", "personality-historical", "coverage"),
    Query("Q6", "secure base safe haven established adult romantic relationships",
          "empirical-journal", "attachment-relational", "coverage"),
    Query("Q7", "Basson responsive sexual desire model spontaneous desire",
          "empirical-journal", "sexology", "coverage"),
    Query("Q8", "shared novel activity self-expansion relationship maintenance",
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_queries.py -v`
Expected: PASS, 6 tests

- [ ] **Step 5: Write the failing tests for `schema.py`**

`probe/tests/test_schema.py`:

```python
import unittest

from probe.schema import CellRecord, validate


def _rec(**over):
    base = dict(
        connector="crossref",
        query_id="Q1",
        result="hit",
        n_results=12,
        top_result="Some Paper — Author — 2021",
        venue_class="peer-reviewed-article",
        doi_present=True,
        metadata_completeness=("doi", "type", "venue"),
        notes="",
        retrieved_at="2026-08-15T00:00:00Z",
    )
    base.update(over)
    return CellRecord(**base)


class TestValidate(unittest.TestCase):
    def test_valid_record_has_no_problems(self):
        self.assertEqual(validate(_rec()), [])

    def test_rejects_unknown_result(self):
        problems = validate(_rec(result="maybe"))
        self.assertTrue(any("result" in p for p in problems))

    def test_rejects_unknown_venue_class(self):
        problems = validate(_rec(venue_class="journal"))
        self.assertTrue(any("venue_class" in p for p in problems))

    def test_rejects_negative_n_results(self):
        problems = validate(_rec(n_results=-1))
        self.assertTrue(any("n_results" in p for p in problems))

    def test_rejects_unknown_metadata_key(self):
        problems = validate(_rec(metadata_completeness=("doi", "vibes")))
        self.assertTrue(any("vibes" in p for p in problems))

    def test_hit_must_record_top_result(self):
        problems = validate(_rec(top_result=None))
        self.assertTrue(any("top_result" in p for p in problems))

    def test_miss_with_results_requires_a_note(self):
        """Spec section 4: C2 adjacent-match must be explained, not silently scored."""
        problems = validate(_rec(result="miss", n_results=7, top_result=None,
                                 venue_class="unverified", notes=""))
        self.assertTrue(any("note" in p for p in problems))

    def test_miss_with_results_and_a_note_is_valid(self):
        rec = _rec(result="miss", n_results=7, top_result=None,
                   venue_class="unverified", doi_present=False,
                   metadata_completeness=(),
                   notes="token search returned adjacent papers; no construct match")
        self.assertEqual(validate(rec), [])

    def test_clean_miss_is_valid(self):
        rec = _rec(result="miss", n_results=0, top_result=None,
                   venue_class="unverified", doi_present=False,
                   metadata_completeness=(), notes="")
        self.assertEqual(validate(rec), [])

    def test_to_dict_is_json_serialisable(self):
        import json
        json.dumps(_rec().to_dict())
```

- [ ] **Step 6: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_schema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'probe.schema'`

- [ ] **Step 7: Implement `probe/schema.py`**

```python
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
```

- [ ] **Step 8: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_schema.py -v`
Expected: PASS, 10 tests

- [ ] **Step 9: Write the failing tests for `connectors/base.py`**

`probe/tests/test_base.py`:

```python
import time
import unittest

from probe.connectors.base import Item, RateLimiter, Response, build_headers, build_url


class TestBuildUrl(unittest.TestCase):
    def test_no_params_returns_url_unchanged(self):
        self.assertEqual(build_url("https://api.example.com/works", None),
                         "https://api.example.com/works")

    def test_params_are_appended_and_encoded(self):
        url = build_url("https://api.example.com/works", {"query": "a b", "rows": 5})
        self.assertIn("query=a+b", url)
        self.assertIn("rows=5", url)
        self.assertTrue(url.startswith("https://api.example.com/works?"))

    def test_bracketed_filter_params_survive_encoding(self):
        """OSF uses filter[provider]; the server must still receive the brackets."""
        url = build_url("https://api.osf.io/v2/preprints/", {"filter[provider]": "psyarxiv"})
        self.assertIn("filter%5Bprovider%5D=psyarxiv", url)


class TestBuildHeaders(unittest.TestCase):
    def test_always_sets_user_agent_and_accept(self):
        h = build_headers()
        self.assertIn("User-Agent", h)
        self.assertEqual(h["Accept"], "application/json")

    def test_extra_headers_are_merged(self):
        h = build_headers({"x-api-key": "abc"})
        self.assertEqual(h["x-api-key"], "abc")
        self.assertIn("User-Agent", h)


class TestRateLimiter(unittest.TestCase):
    def test_first_call_does_not_block(self):
        limiter = RateLimiter(0.5)
        start = time.monotonic()
        limiter.wait()
        self.assertLess(time.monotonic() - start, 0.1)

    def test_second_call_waits_the_interval(self):
        limiter = RateLimiter(0.2)
        limiter.wait()
        start = time.monotonic()
        limiter.wait()
        self.assertGreaterEqual(time.monotonic() - start, 0.15)


class TestItem(unittest.TestCase):
    def test_item_defaults_are_all_none_or_empty(self):
        item = Item()
        self.assertIsNone(item.doi)
        self.assertEqual(item.authors, ())
        self.assertEqual(item.extra_ids, {})

    def test_response_carries_total_items_and_raw(self):
        r = Response(total=3, items=[Item(title="x")], raw={"k": "v"})
        self.assertEqual(r.total, 3)
        self.assertEqual(r.items[0].title, "x")
        self.assertEqual(r.raw["k"], "v")
```

- [ ] **Step 10: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_base.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'probe.connectors.base'`

- [ ] **Step 11: Implement `probe/connectors/base.py`**

```python
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
```

- [ ] **Step 12: Run the full suite**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests -v`
Expected: PASS, 25 tests

- [ ] **Step 13: Implement `probe/run.py` with all five connectors pre-declared**

This is ADR-005's Phase 0 namespace refactor. The registry names all five connectors **now**, so no Task 3–7 agent ever edits this file. Modules are imported lazily, so a name whose module does not exist yet simply fails when that connector is run — not at import time.

```python
"""Run one connector's 12 cells and write validated records to results/.

The registry below names all five connectors up front so that parallel
per-connector work never shares a write to this file (ADR-005 Phase 0).
Modules are imported lazily; a connector whose module is not yet written
fails only when it is run.
"""

from __future__ import annotations

import argparse
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .queries import QUERIES
from .schema import CellRecord, validate

# connector name -> module name under probe.connectors
CONNECTORS: dict[str, str] = {
    "semantic-scholar": "semantic_scholar",
    "openalex": "openalex",
    "crossref": "crossref",
    "europe-pmc": "europe_pmc",
    "psyarxiv-osf": "osf",
}

RESULTS_DIR = Path(__file__).parent / "results"


def load(name: str):
    module = importlib.import_module(f".connectors.{CONNECTORS[name]}", package="probe")
    if module.NAME != name:
        raise AssertionError(f"{CONNECTORS[name]}.NAME is {module.NAME!r}, expected {name!r}")
    return module


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _describe(item) -> str:
    authors = ", ".join(item.authors[:3]) or "unknown"
    return f"{item.title} — {authors} — {item.year}"


def run_connector(name: str) -> list[CellRecord]:
    module = load(name)
    records: list[CellRecord] = []

    for query in QUERIES:
        resp = module.search(query.search)
        top = resp.items[0] if resp.items else None
        rec = CellRecord(
            connector=name,
            query_id=query.id,
            result="hit" if top else "miss",
            n_results=resp.total,
            top_result=_describe(top) if top else None,
            venue_class="unverified",   # classified by hand per RUBRIC.md
            doi_present=bool(top and top.doi),
            metadata_completeness=(),   # filled in by hand per RUBRIC.md
            notes="",
            retrieved_at=_now(),
        )
        records.append(rec)
        print(f"{name} {query.id}: n={resp.total} top={rec.top_result}")

    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--connector", required=True, choices=sorted(CONNECTORS))
    args = parser.parse_args()

    records = run_connector(args.connector)
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{args.connector}.json"
    out.write_text(
        json.dumps([r.to_dict() for r in records], indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nwrote {out} ({len(records)} cells)")


if __name__ == "__main__":
    main()
```

`run_connector` produces a **first pass** — what came back mechanically. `venue_class`, `metadata_completeness`, `partial` downgrades, and the C2 adjacent-match note are judgement calls made per `RUBRIC.md` while writing the dossier, and edited into the results JSON by hand.

Verify the registry resolves and the CLI rejects unknown names:

```bash
cd docs/research/connectors
python3 -c "from probe.run import CONNECTORS; print(sorted(CONNECTORS)); assert len(CONNECTORS)==5"
python3 -m probe.run --connector nope 2>&1 | tail -1   # expect: invalid choice
```

Expected: the five names, then an `invalid choice` error.

- [ ] **Step 14: Write `probe/RUBRIC.md`**

Five agents classifying independently will diverge, and Task 8's matrix compares them. This file is passed **verbatim** to every Task 3–7 agent.

````markdown
# Classification rubric

Applied when hand-refining `probe/results/<connector>.json`. Deviating from this
is a review finding — Task 8 compares these classifications across connectors.

## `venue_class` — classify the TOP result only

Decide from the item's own registered metadata, never from the URL or the index
that surfaced it.

| Observed | Class |
|---|---|
| Registered type is a journal article in a named journal | `peer-reviewed-article` |
| Registered type is a book or monograph, or an ISBN with no chapter | `book` |
| A chapter within a larger work | `book-chapter` |
| Published by a modality institute or professional body, not a journal | `institute-publication` |
| Preprint server, or type `posted-content` / source `PPR` | `preprint` |
| Clinical guideline or consensus statement | `guideline` |
| Report, thesis, working paper, org web content | `grey` |
| Editorial, commentary, letter, blog, consumer media | `commentary` |
| **No DOI, or no registered type to classify from** | `unverified` |

When two classes could apply, choose the **more specific** one and say why in `notes`.
When genuinely undecidable, use `unverified` and say so — do not guess.

## `metadata_completeness` — what the API ACTUALLY returned

List only keys present and non-null **in the payload for that query**. Do not list a
key because the API documents it.

Registry keys: `doi` `pmid` `pmcid` `openalex_id` `semantic_scholar_id` `osf_id`
`arxiv_id` `isbn` `issn`
Envelope fields: `type` `venue` `publisher` `retraction_status` `oa_status`

## `result`

- `hit` — a top result that genuinely addresses the query
- `partial` — results returned, but the top one is tangential, wrong population,
  or wrong literature (say which in `notes`)
- `miss` — nothing addressing the query, regardless of `n_results`

## C2 (negative control)

Zero results → `miss`, `n_results: 0`. Non-empty with no construct match → `miss`
plus the note `"token search returned adjacent papers; no construct match"`. A result
presented as matching the fabricated construct or its citation → **record it in the
dossier §7 as a finding**, not merely as a cell.
````

- [ ] **Step 15: Commit**

```bash
git add docs/research/connectors/probe/
git commit -m "feat(probe): shared harness, pre-declared registry, classification rubric

Stdlib-only discovery harness. queries.py transcribes the frozen benchmark;
schema.py encodes the cell contract including the C2 adjacent-match rule
(a miss with n_results > 0 must carry a note); base.py provides Item,
Response, RateLimiter and pure URL/header builders.

run.py declares all five connectors up front with lazy import - ADR-005
Phase 0, so the five parallel per-connector tasks never share a write.
RUBRIC.md fixes venue-class and metadata-completeness judgement so the
five dossiers stay comparable in the Task 8 matrix.

Deliberately minimal - this is disposable discovery tooling, not
psychology-mcp code.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Semantic Scholar — adapter and dossier

**Files:**
- Create: `docs/research/connectors/probe/connectors/semantic_scholar.py`, `docs/research/connectors/01-semantic-scholar.md`
- Test: `probe/tests/test_semantic_scholar.py`
- Data: `probe/fixtures/semantic-scholar-C1.json`, `probe/results/semantic-scholar.json`

**Interfaces:**
- Consumes (read-only): `queries.QUERIES`, `schema.CellRecord`, `schema.validate`, `connectors.base.{Item, Response, RateLimiter, http_get_json}`, `run.py`, `RUBRIC.md`
- Produces:
  - `connectors.semantic_scholar.NAME = "semantic-scholar"`, `.RATE: float`, `.search(query: str, limit: int = 10) -> Response`, `.parse(raw: dict) -> Response`

- [ ] **Step 1: Observe the live response and record a fixture**

The endpoint and field list below are from documentation knowledge and **must be verified**, per spec Appendix A's "not verified" list.

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research/docs/research/connectors
curl -s -A "open-biosciences-connector-probe/1.0" \
  'https://api.semanticscholar.org/graph/v1/paper/search?query=emotionally+focused+therapy+couples+evidence-based+outcome&limit=5&fields=title,year,authors,externalIds,venue,publicationTypes,publicationVenue,openAccessPdf' \
  | python3 -m json.tool > probe/fixtures/semantic-scholar-C1.json
head -40 probe/fixtures/semantic-scholar-C1.json
```

Expected: JSON with `total`, `offset`, `data[]`. If the shape differs, correct Step 3's parser to match what you observe — **the observed shape wins over this plan.** Record rate-limit behaviour and any key requirement for dossier §1.

- [ ] **Step 2: Write the failing parser test**

`probe/tests/test_semantic_scholar.py`:

```python
import json
import unittest
from pathlib import Path

from probe.connectors import semantic_scholar as s2

FIXTURE = Path(__file__).parent.parent / "fixtures" / "semantic-scholar-C1.json"


class TestSemanticScholarParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(s2.NAME, "semantic-scholar")
        self.assertGreater(s2.RATE, 0)

    def test_parse_returns_a_response(self):
        resp = s2.parse(self.raw)
        self.assertGreaterEqual(resp.total, 0)
        self.assertIsInstance(resp.items, list)
        self.assertIs(resp.raw, self.raw)

    def test_items_carry_a_title(self):
        resp = s2.parse(self.raw)
        self.assertTrue(resp.items, "C1 fixture should contain at least one result")
        self.assertTrue(resp.items[0].title)

    def test_doi_is_lifted_out_of_external_ids(self):
        resp = s2.parse(self.raw)
        dois = [i.doi for i in resp.items if i.doi]
        self.assertTrue(dois, "at least one C1 result should carry a DOI")
        self.assertTrue(all("/" in d for d in dois), "a DOI contains a slash")

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = s2.parse({"total": 0, "data": []})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_semantic_scholar.py -v`
Expected: FAIL — `ImportError: cannot import name 'semantic_scholar'`

- [ ] **Step 4: Implement the adapter**

`probe/connectors/semantic_scholar.py` — **adjust field paths to the fixture you actually recorded**:

```python
"""Semantic Scholar Academic Graph adapter."""

from __future__ import annotations

from .base import Item, RateLimiter, Response, http_get_json

NAME = "semantic-scholar"
BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
RATE = 3.0  # unauthenticated shared pool is heavily throttled; be conservative
FIELDS = "title,year,authors,externalIds,venue,publicationTypes,publicationVenue,openAccessPdf"

_limiter = RateLimiter(RATE)


def parse(raw: dict) -> Response:
    items: list[Item] = []
    for rec in raw.get("data") or []:
        ext = rec.get("externalIds") or {}
        venue_obj = rec.get("publicationVenue") or {}
        types = rec.get("publicationTypes") or []
        items.append(
            Item(
                title=rec.get("title"),
                authors=tuple(a.get("name", "") for a in (rec.get("authors") or [])),
                year=rec.get("year"),
                doi=ext.get("DOI"),
                type=types[0] if types else None,
                venue=rec.get("venue") or venue_obj.get("name"),
                publisher=venue_obj.get("publisher"),
                oa_status="open" if rec.get("openAccessPdf") else None,
                extra_ids={
                    k: v for k, v in {
                        "semantic_scholar_id": rec.get("paperId"),
                        "pmid": ext.get("PubMed"),
                        "pmcid": ext.get("PubMedCentral"),
                        "arxiv_id": ext.get("ArXiv"),
                    }.items() if v
                },
            )
        )
    return Response(total=raw.get("total", len(items)), items=items, raw=raw)


def search(query: str, limit: int = 10) -> Response:
    _limiter.wait()
    raw = http_get_json(BASE, {"query": query, "limit": limit, "fields": FIELDS})
    return parse(raw)
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_semantic_scholar.py -v`
Expected: PASS, 5 tests

- [ ] **Step 6: Run the 12 cells**

```bash
cd docs/research/connectors
export PROBE_CONTACT_EMAIL="dwbranson@gmail.com"
python3 -m probe.run --connector semantic-scholar
```

Expected: 12 printed lines, then `wrote probe/results/semantic-scholar.json (12 cells)`. If the API throttles (HTTP 429), raise `RATE` in the adapter and re-run — record the observed limit for dossier §1.

- [ ] **Step 7: Hand-refine the records, then re-validate**

Edit `probe/results/semantic-scholar.json`: set each `venue_class` from the observed record, list the `metadata_completeness` keys the payload actually carried, downgrade thin results to `partial`, and apply the C2 rule from `README.md` — if C2 returned adjacent papers with no construct match, set `result: "miss"` and add the note.

```bash
cd docs/research/connectors
python3 -c "
import json
from probe.schema import CellRecord, validate
rows = json.load(open('probe/results/semantic-scholar.json'))
bad = 0
for r in rows:
    r['metadata_completeness'] = tuple(r['metadata_completeness'])
    for p in validate(CellRecord(**r)):
        print(r['query_id'], p); bad += 1
print('OK' if not bad else f'{bad} problem(s)')
"
```

Expected: `OK`

- [ ] **Step 8: Write `01-semantic-scholar.md`**

Use the spec §5 template, all eight sections. Section 4 is the 12 cells as a markdown table with example records. Sections 5 and 6 answer Fuzzy-to-Fact feasibility (does it accept a DOI as a lookup key for `get_work`?) and FastMCP wrapping feasibility (async-native REST? batch endpoint? is a slim projection expressible via the `fields` parameter?). Section 7 records whether a public MCP server exists. Section 8 gives an unambiguous wrap / bind / drop recommendation.

- [ ] **Step 9: Commit**

```bash
git add docs/research/connectors/
git commit -m "feat(probe): Semantic Scholar adapter, runner, and dossier 01

Records the C1 fixture, parses it into normalised Items, and fills all 12
cells. Dossier covers mechanics, measured coverage, Fuzzy-to-Fact and
FastMCP wrapping feasibility, existing-server check, and a wrap/bind/drop
recommendation.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: OpenAlex — adapter and dossier

**Files:**
- Create: `docs/research/connectors/probe/connectors/openalex.py`, `docs/research/connectors/02-openalex.md`
- Test: `probe/tests/test_openalex.py`
- Data: `probe/fixtures/openalex-C1.json`, `probe/results/openalex.json`

**Interfaces:**
- Consumes (read-only): `connectors.base.{Item, RateLimiter, Response, http_get_json}`, `queries.QUERIES`, `schema.*`, `run.py`, `RUBRIC.md`
- Produces: `connectors.openalex.NAME = "openalex"`, `.RATE`, `.search(query, limit)`, `.parse(raw)`

- [ ] **Step 1: Record the fixture**

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research/docs/research/connectors
curl -s -A "open-biosciences-connector-probe/1.0 mailto:dwbranson@gmail.com" \
  'https://api.openalex.org/works?search=emotionally+focused+therapy+couples+evidence-based+outcome&per-page=5&mailto=dwbranson@gmail.com' \
  | python3 -m json.tool > probe/fixtures/openalex-C1.json
head -60 probe/fixtures/openalex-C1.json
```

Expected: `meta.count`, `results[]` with `id`, `doi`, `title`/`display_name`, `type`, `publication_year`, `primary_location.source`, `open_access`, `is_retracted`. **Note `is_retracted` specifically** — if present, OpenAlex answers spec §10 open question 3 for free.

- [ ] **Step 2: Write the failing parser test**

`probe/tests/test_openalex.py`:

```python
import json
import unittest
from pathlib import Path

from probe.connectors import openalex

FIXTURE = Path(__file__).parent.parent / "fixtures" / "openalex-C1.json"


class TestOpenAlexParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(openalex.NAME, "openalex")
        self.assertGreater(openalex.RATE, 0)

    def test_total_comes_from_meta_count(self):
        resp = openalex.parse(self.raw)
        self.assertEqual(resp.total, self.raw["meta"]["count"])

    def test_doi_is_bare_not_a_url(self):
        """OpenAlex returns https://doi.org/10.x; a DOI field should hold 10.x."""
        resp = openalex.parse(self.raw)
        dois = [i.doi for i in resp.items if i.doi]
        self.assertTrue(dois)
        self.assertTrue(all(d.startswith("10.") for d in dois))

    def test_type_is_captured_for_venue_classification(self):
        resp = openalex.parse(self.raw)
        self.assertTrue(any(i.type for i in resp.items))

    def test_retraction_status_is_captured_when_present(self):
        resp = openalex.parse(self.raw)
        if "is_retracted" in (self.raw["results"][0] if self.raw["results"] else {}):
            self.assertIn(resp.items[0].retraction_status, ("retracted", "not-retracted"))

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = openalex.parse({"meta": {"count": 0}, "results": []})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_openalex.py -v`
Expected: FAIL — `ImportError: cannot import name 'openalex'`

- [ ] **Step 4: Implement the adapter**

```python
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
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_openalex.py -v`
Expected: PASS, 6 tests

- [ ] **Step 6: Run the 12 cells, refine, validate**

```bash
cd docs/research/connectors
python3 -m probe.run --connector openalex
```

Then hand-refine `probe/results/openalex.json` as in Task 3 Step 7, and re-validate with the same one-liner, substituting the filename. Expected: `OK`.

- [ ] **Step 7: Write `02-openalex.md`** using the spec §5 template, all eight sections.

- [ ] **Step 8: Commit**

```bash
git add docs/research/connectors/
git commit -m "feat(probe): OpenAlex adapter and dossier 02

Normalises DOIs to bare form, captures type for venue classification, and
records is_retracted where present - which bears directly on spec open
question 3 (whether retraction needs a second Crossref lookup).

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Crossref — adapter and dossier

Crossref is structurally load-bearing, not merely another index: spec §6.2 resolves `venue_class` from registered metadata, and §3.5 names Crossref the authoritative source for it. Dossier §3 matters more here than coverage does.

**Files:**
- Create: `docs/research/connectors/probe/connectors/crossref.py`, `docs/research/connectors/03-crossref.md`
- Test: `probe/tests/test_crossref.py`
- Data: `probe/fixtures/crossref-C1.json`, `probe/results/crossref.json`

**Interfaces:**
- Consumes (read-only): `connectors.base.*`, `queries.QUERIES`, `schema.*`, `run.py`, `RUBRIC.md`
- Produces: `connectors.crossref.NAME = "crossref"`, `.RATE`, `.search(query, limit)`, `.parse(raw)`

- [ ] **Step 1: Record the fixture**

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research/docs/research/connectors
curl -s -A "open-biosciences-connector-probe/1.0 mailto:dwbranson@gmail.com" \
  'https://api.crossref.org/works?query=emotionally+focused+therapy+couples+evidence-based+outcome&rows=5&mailto=dwbranson@gmail.com' \
  | python3 -m json.tool > probe/fixtures/crossref-C1.json
head -60 probe/fixtures/crossref-C1.json
```

Expected: `message.total-results`, `message.items[]` with `DOI`, `title[]`, `type`, `container-title[]`, `publisher`, `issued.date-parts`, `ISBN`, `ISSN`, and possibly `update-to` / `relation` for retractions.

**Also record the distinct `type` values Crossref emits** — `journal-article`, `book`, `book-chapter`, `posted-content`, `monograph`, `report` — since spec §6.2's venue classes map onto them:

```bash
python3 -c "
import json
raw = json.load(open('probe/fixtures/crossref-C1.json'))
print(sorted({i.get('type') for i in raw['message']['items']}))
"
```

- [ ] **Step 2: Write the failing parser test**

`probe/tests/test_crossref.py`:

```python
import json
import unittest
from pathlib import Path

from probe.connectors import crossref

FIXTURE = Path(__file__).parent.parent / "fixtures" / "crossref-C1.json"


class TestCrossrefParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(crossref.NAME, "crossref")
        self.assertGreater(crossref.RATE, 0)

    def test_total_comes_from_message_total_results(self):
        resp = crossref.parse(self.raw)
        self.assertEqual(resp.total, self.raw["message"]["total-results"])

    def test_title_is_flattened_from_the_list(self):
        resp = crossref.parse(self.raw)
        self.assertIsInstance(resp.items[0].title, str)

    def test_every_item_carries_a_doi(self):
        """Crossref is the DOI registry; a result without a DOI is a parser bug."""
        resp = crossref.parse(self.raw)
        self.assertTrue(all(i.doi for i in resp.items))

    def test_type_and_publisher_are_captured(self):
        """Spec section 6.2 classifies venue from registered type and publisher."""
        resp = crossref.parse(self.raw)
        self.assertTrue(resp.items[0].type)
        self.assertTrue(resp.items[0].publisher)

    def test_isbn_and_issn_land_in_extra_ids_when_present(self):
        resp = crossref.parse(self.raw)
        for item, rec in zip(resp.items, self.raw["message"]["items"]):
            if rec.get("ISBN"):
                self.assertIn("isbn", item.extra_ids)
            if rec.get("ISSN"):
                self.assertIn("issn", item.extra_ids)

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = crossref.parse({"message": {"total-results": 0, "items": []}})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_crossref.py -v`
Expected: FAIL — `ImportError: cannot import name 'crossref'`

- [ ] **Step 4: Implement the adapter**

```python
"""Crossref adapter. The DOI registry — authoritative for venue class per spec 6.2."""

from __future__ import annotations

import os

from .base import Item, RateLimiter, Response, http_get_json

NAME = "crossref"
BASE = "https://api.crossref.org/works"
RATE = 0.2  # polite pool; back off on 429
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
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_crossref.py -v`
Expected: PASS, 7 tests

- [ ] **Step 6: Run the 12 cells, refine, validate**

```bash
cd docs/research/connectors && python3 -m probe.run --connector crossref
```

Refine and re-validate as in Task 3 Step 7. Expected: `OK`.

- [ ] **Step 7: Write `03-crossref.md`**

All eight sections. Give §3 extra weight: tabulate every Crossref `type` value observed across all 12 queries against spec §6.2's venue classes, and state explicitly which classes Crossref can and cannot resolve. This table is the input to Task 9.

- [ ] **Step 8: Commit**

```bash
git add docs/research/connectors/
git commit -m "feat(probe): Crossref adapter and dossier 03

Crossref is structurally load-bearing, not just another index: spec 6.2
resolves venue_class from registered metadata and names Crossref the
authoritative source. Dossier section 3 maps observed Crossref type values
onto the venue classes and states what it cannot resolve.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Europe PMC — adapter and dossier

The open question here is **supersede vs. complement** (spec §10 q1): Europe PMC's scope includes PubMed records plus preprints and NCBI Bookshelf monographs. Dossier §7 must answer whether it replaces a PubMed binding.

**Files:**
- Create: `docs/research/connectors/probe/connectors/europe_pmc.py`, `docs/research/connectors/04-europe-pmc.md`
- Test: `probe/tests/test_europe_pmc.py`
- Data: `probe/fixtures/europe-pmc-C1.json`, `probe/results/europe-pmc.json`

**Interfaces:**
- Consumes (read-only): `connectors.base.*`, `queries.QUERIES`, `schema.*`, `run.py`, `RUBRIC.md`
- Produces: `connectors.europe_pmc.NAME = "europe-pmc"`, `.RATE`, `.search(query, limit)`, `.parse(raw)`

- [ ] **Step 1: Record the fixture**

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research/docs/research/connectors
curl -s -A "open-biosciences-connector-probe/1.0" \
  'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=emotionally%20focused%20therapy%20couples%20evidence-based%20outcome&format=json&pageSize=5&resultType=core' \
  | python3 -m json.tool > probe/fixtures/europe-pmc-C1.json
head -60 probe/fixtures/europe-pmc-C1.json
```

Expected: `hitCount`, `resultList.result[]` with `id`, `source`, `pmid`, `pmcid`, `doi`, `title`, `authorString`, `journalTitle`, `pubYear`, `pubType`, `isOpenAccess`. **Record the distinct `source` values** (`MED`, `PPR`, `CTX`, `NBK`) — `PPR` is preprints and `NBK` is Bookshelf, which is the evidence for the supersede question.

- [ ] **Step 2: Write the failing parser test**

`probe/tests/test_europe_pmc.py`:

```python
import json
import unittest
from pathlib import Path

from probe.connectors import europe_pmc

FIXTURE = Path(__file__).parent.parent / "fixtures" / "europe-pmc-C1.json"


class TestEuropePmcParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(europe_pmc.NAME, "europe-pmc")
        self.assertGreater(europe_pmc.RATE, 0)

    def test_total_comes_from_hit_count(self):
        resp = europe_pmc.parse(self.raw)
        self.assertEqual(resp.total, self.raw["hitCount"])

    def test_pmid_and_pmcid_land_in_extra_ids(self):
        resp = europe_pmc.parse(self.raw)
        ids = [i.extra_ids for i in resp.items]
        self.assertTrue(any("pmid" in d for d in ids))

    def test_author_string_is_split_into_a_tuple(self):
        resp = europe_pmc.parse(self.raw)
        self.assertIsInstance(resp.items[0].authors, tuple)

    def test_year_is_an_int(self):
        resp = europe_pmc.parse(self.raw)
        years = [i.year for i in resp.items if i.year is not None]
        self.assertTrue(all(isinstance(y, int) for y in years))

    def test_preprint_source_maps_to_preprint_type(self):
        """source=PPR is Europe PMC's preprint marker; it must survive parsing."""
        resp = europe_pmc.parse(
            {"hitCount": 1, "resultList": {"result": [
                {"id": "PPR1", "source": "PPR", "title": "t", "pubYear": "2024"}]}}
        )
        self.assertEqual(resp.items[0].type, "preprint")

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = europe_pmc.parse({"hitCount": 0, "resultList": {"result": []}})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_europe_pmc.py -v`
Expected: FAIL — `ImportError: cannot import name 'europe_pmc'`

- [ ] **Step 4: Implement the adapter**

```python
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
        items.append(
            Item(
                title=rec.get("title"),
                authors=tuple(
                    a.strip() for a in (rec.get("authorString") or "").split(",") if a.strip()
                ),
                year=_int_or_none(rec.get("pubYear")),
                doi=rec.get("doi"),
                type=_SOURCE_TYPE.get(rec.get("source"), rec.get("pubType")),
                venue=rec.get("journalTitle"),
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
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_europe_pmc.py -v`
Expected: PASS, 7 tests

- [ ] **Step 6: Run the 12 cells, refine, validate**

```bash
cd docs/research/connectors && python3 -m probe.run --connector europe-pmc
```

Refine and re-validate as in Task 3 Step 7. Expected: `OK`.

- [ ] **Step 7: Write `04-europe-pmc.md`**

All eight sections. §7 must answer spec §10 open question 1 directly: tabulate the `source` values observed across all 12 queries, and state whether Europe PMC supersedes a PubMed binding or complements it — with the `PPR`/`NBK` counts as evidence.

- [ ] **Step 8: Commit**

```bash
git add docs/research/connectors/
git commit -m "feat(probe): Europe PMC adapter and dossier 04

Maps Europe PMC source codes (MED/PPR/NBK) onto item types so preprint and
Bookshelf coverage is measurable. Dossier section 7 answers the
supersede-vs-complement question against a PubMed binding.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: PsyArXiv / OSF — adapter and dossier

**Files:**
- Create: `docs/research/connectors/probe/connectors/osf.py`, `docs/research/connectors/05-psyarxiv-osf.md`
- Test: `probe/tests/test_osf.py`
- Data: `probe/fixtures/psyarxiv-osf-C1.json`, `probe/results/psyarxiv-osf.json`

**Interfaces:**
- Consumes (read-only): `connectors.base.*`, `queries.QUERIES`, `schema.*`, `run.py`, `RUBRIC.md`
- Produces: `connectors.osf.NAME = "psyarxiv-osf"`, `.RATE`, `.search(query, limit)`, `.parse(raw)`

- [ ] **Step 1: Record the fixture**

OSF uses JSON:API, so the shape differs from the other four — `data[]` with `attributes` and `relationships`.

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research/docs/research/connectors
curl -s -A "open-biosciences-connector-probe/1.0" \
  'https://api.osf.io/v2/preprints/?filter%5Bprovider%5D=psyarxiv&filter%5Btitle%5D=emotionally%20focused%20therapy&page%5Bsize%5D=5' \
  | python3 -m json.tool > probe/fixtures/psyarxiv-osf-C1.json
head -80 probe/fixtures/psyarxiv-osf-C1.json
```

Expected: `links.meta.total`, `data[]` with `id`, `attributes.title`, `attributes.date_published`, `attributes.doi`, `attributes.is_published`.

**If `filter[title]` is not supported, or full-text search requires a different route**, record what does work and correct Step 4. OSF's search surface differs materially from a scholarly index — that difference is itself a dossier §5/§6 finding, not a blocker.

- [ ] **Step 2: Write the failing parser test**

`probe/tests/test_osf.py`:

```python
import json
import unittest
from pathlib import Path

from probe.connectors import osf

FIXTURE = Path(__file__).parent.parent / "fixtures" / "psyarxiv-osf-C1.json"


class TestOsfParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_name_and_rate_declared(self):
        self.assertEqual(osf.NAME, "psyarxiv-osf")
        self.assertGreater(osf.RATE, 0)

    def test_parses_jsonapi_data_array(self):
        resp = osf.parse(self.raw)
        self.assertIsInstance(resp.items, list)
        self.assertIs(resp.raw, self.raw)

    def test_every_item_is_typed_as_a_preprint(self):
        """Everything from this route is a preprint by construction."""
        resp = osf.parse(self.raw)
        self.assertTrue(all(i.type == "preprint" for i in resp.items))

    def test_osf_id_lands_in_extra_ids(self):
        resp = osf.parse(self.raw)
        if resp.items:
            self.assertIn("osf_id", resp.items[0].extra_ids)

    def test_year_is_extracted_from_iso_date_published(self):
        resp = osf.parse(
            {"data": [{"id": "abc", "attributes": {
                "title": "t", "date_published": "2023-04-01T00:00:00.000000Z"}}]}
        )
        self.assertEqual(resp.items[0].year, 2023)

    def test_parse_of_empty_payload_is_a_clean_zero(self):
        resp = osf.parse({"data": []})
        self.assertEqual(resp.total, 0)
        self.assertEqual(resp.items, [])
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_osf.py -v`
Expected: FAIL — `ImportError: cannot import name 'osf'`

- [ ] **Step 4: Implement the adapter**

```python
"""PsyArXiv via the OSF Preprints API (JSON:API). Everything from this route
is a preprint by construction, which is why type is set unconditionally.
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
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd docs/research/connectors && python3 -m pytest probe/tests/test_osf.py -v`
Expected: PASS, 6 tests

- [ ] **Step 6: Run the 12 cells, refine, validate**

```bash
cd docs/research/connectors && python3 -m probe.run --connector psyarxiv-osf
```

`filter[title]` is a substring match, not relevance ranking — expect low recall and **record that as a finding**, not as poor coverage. Refine and re-validate as in Task 3 Step 7. Expected: `OK`.

- [ ] **Step 7: Write `05-psyarxiv-osf.md`**

All eight sections. §3 must include the Crossref cross-check from spec §3.5: for each PsyArXiv result carrying a DOI, compare the metadata OSF returns against what Crossref returns for the same DOI, and report how much preprint metadata survives across indexers. §5 must be candid about whether substring filtering can support Fuzzy-to-Fact Phase 1 at all.

- [ ] **Step 8: Commit**

```bash
git add docs/research/connectors/
git commit -m "feat(probe): PsyArXiv/OSF adapter and dossier 05

OSF is JSON:API and filters by substring rather than ranking relevance, so
low recall here is a search-surface finding rather than a coverage gap.
Dossier section 3 cross-checks preprint metadata against Crossref for the
same DOIs.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Coverage matrix

**Files:**
- Create: `docs/research/connectors/00-coverage-matrix.md`

**Interfaces:**
- Consumes: `probe/results/*.json` (5 files, 12 records each) and each dossier's §4
- Produces: the aggregated matrix that Tasks 9 and 10 read

- [ ] **Step 1: Verify all 60 cells exist and validate**

```bash
cd docs/research/connectors
python3 -c "
import json, glob
from probe.schema import CellRecord, validate
total = 0; bad = 0
for path in sorted(glob.glob('probe/results/*.json')):
    rows = json.load(open(path))
    total += len(rows)
    print(f'{path}: {len(rows)} cells')
    for r in rows:
        r['metadata_completeness'] = tuple(r['metadata_completeness'])
        for p in validate(CellRecord(**r)):
            print('  ', r['query_id'], p); bad += 1
print(f'TOTAL {total} cells, {bad} problem(s)')
"
```

Expected: `TOTAL 60 cells, 0 problem(s)`. Anything less than 60 means a connector was skipped — spec §11 forbids a blank or "not attempted" cell.

- [ ] **Step 2: Write `00-coverage-matrix.md`**

Structure:

1. **The matrix** — 12 rows (Q1–Q10, C1, C2) × 5 connector columns, each cell `hit`/`partial`/`miss` with `n` and whether a DOI came back.
2. **Control results** — C1 per connector (harness validation) and C2 per connector scored by the README's three-outcome rule, stated separately from coverage.
3. **Coverage by format axis** — which connectors reach monograph/book canon (Q4) and historical primaries (Q5). Expect these to be the sparse columns.
4. **Coverage by subject axis** — whether clinical (Q1–Q3), relational (Q6–Q8), and quantitative/cognitive (Q9–Q10) diverge per connector.
5. **Metadata completeness matrix** — connectors × the §6.3 registry keys and §6.2 envelope fields. **This is the table Task 9 consumes.**
6. **Gaps no connector fills** — the honest negative result, which feeds `DECISION.md` §7.5.

- [ ] **Step 3: Commit**

```bash
git add docs/research/connectors/00-coverage-matrix.md
git commit -m "docs(connectors): aggregate the 60-cell coverage matrix

All five connectors across the 12 frozen queries, with controls scored
separately from coverage, breakdowns by format and subject axis, the
metadata-completeness matrix that drives the envelope design, and the gaps
no connector fills.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: Literature envelope

**Files:**
- Create: `docs/research/connectors/06-literature-envelope.md`

**Interfaces:**
- Consumes: `00-coverage-matrix.md` §5 (metadata completeness) and each dossier's §3
- Produces: the Layer-2 response contract that `DECISION.md` §7.1's roster is justified against

- [ ] **Step 1: Write `06-literature-envelope.md`**

Per spec §6 and the ADR conformance map in spec §2.1. Required content:

1. **The two axes** — venue class (Axis A, what it is) and discovery route (Axis B, which connector found it, **never contributing to tier**), with the rationale that an index is a lookup vehicle rather than a peer-review warrant.
2. **Venue classes and their resolution** — the nine classes from spec §6.2, and a mapping table from each connector's observed `type` values (Crossref's especially, from dossier 03 §3) onto them. The three-step resolution order: DOI-with-registered-metadata → domain fallback → `unverified` which must warn.
3. **The literature Key Registry** — the nine keys from spec §6.3, with per-connector availability from the Task 8 matrix, plus null-handling and cardinality following ADR-001 Appendix A.
4. **Retraction status as an envelope field** — and, from spec §10 open question 3, whether it costs one call or two. If OpenAlex's `is_retracted` proved reliable in Task 4, say so; if Crossref is required as a second lookup, say that.
5. **Slim mode** — `doi`, `title`, `venue_class`, with the ADR-001 §7 citation and a note that ADR-001's biomedical triple is `id`/`name`/`score`, so this is an adaptation not an inheritance.
6. **Canonical envelopes** — pagination and error shapes adopted verbatim from ADR-001 §8, including `UNRESOLVED_ENTITY` for a raw string passed to `get_work`.
7. **What stays at Layer 4** — paradigm overrides. The server reports what a thing *is*; the plugin decides what it is *worth*. This split is what makes the envelope reusable by consumers with different editorial policy.

Cite ADR-001 §4, §7, §8, §9 explicitly (spec §11 requires it). Include **no consumer editorial policy** — spec §11 forbids it.

- [ ] **Step 2: Self-check against the acceptance criteria**

```bash
cd docs/research/connectors
grep -c "ADR-001" 06-literature-envelope.md          # expect >= 4
grep -in "paradigm override" 06-literature-envelope.md   # must appear only as Layer-4 exclusion
```

- [ ] **Step 3: Commit**

```bash
git add docs/research/connectors/06-literature-envelope.md
git commit -m "docs(connectors): the Layer-2 literature envelope contract

Venue class decoupled from discovery route, the nine-key literature Key
Registry with per-connector availability, retraction as an envelope field,
the doi/title/venue_class slim triple, and ADR-001 section 8 envelopes
adopted verbatim. Paradigm overrides stay at Layer 4 - the server reports
what a thing is, the plugin decides what it is worth.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: Decision document

**Files:**
- Create: `docs/research/connectors/DECISION.md`

**Interfaces:**
- Consumes: all five dossiers' §8, `00-coverage-matrix.md`, `06-literature-envelope.md`
- Produces: the discovery pass's terminal artefact — the input to a Layer-2 SpecKit program

- [ ] **Step 1: Write `DECISION.md`** — the five sections of spec §7

**§7.1 Server roster and build order.** Which APIs `psychology-mcp` wraps, in tier order — the psychology analog of the biosciences Tier 0–5 table — rolled up from each dossier's §8. Name which are better bound as existing third-party servers than wrapped, with reasoning.

**§7.2 AGE-548 question 3.** Answer from the correctly-read `bio-research` precedent: it declares its own program's gateway (`biosciences-mcp`, `biosciences-mcp-edge`) plus selected public third-party servers (`pubmed`, `biorxiv`, `synapse`). The pattern is *"the plugin declares the platform's first-party gateway, and public third-party servers where they exist."* Credentialed access is not the boundary — `${VAR}` header expansion, `headersHelper`, and `userConfig`/`sensitive` all exist.

**§7.3 Producer/consumer contradictions.** Recorded, not fixed:
- `hci-canon` `.claude/skills/relational-vibrancy/SKILL.md:70` names `pubmed-database / OpenAlex / Europe PMC`; `psychology-research` names `pubmed, semantic-scholar`.
- The same file's frontmatter enumerates seven modalities plus an eighth lens, `:86` says *"omit to run all seven"*, and the 2026-08-14 run report says *"four of the eight lenses."*

**§7.4 Interim plugin binding.** The literal `.mcp.json` content declarable **today**, before `psychology-mcp` exists. Every entry carries `"type": "http"` — an entry with a `url` and no `type` is read as stdio, skipped, and warned about. Note the `psychology-research-plugins` `rsync --delete` mirror: deltas are authored upstream and reach the mirror by that sync, never hand-edited there. **Proposed, not applied.**

**§7.5 What remains unsatisfiable.** If no connector reaches APA/PsycINFO-class content, then `source-tiers.yaml` assigning `apa.org: 1` and the marketplace description promising *"source hierarchy, claim provenance"* both describe reach the plugin cannot deliver. Include the bounded PsycNET reachability check. Any connector with partial coverage gets its partiality named, not averaged away.

- [ ] **Step 2: Verify every acceptance criterion in spec §11**

```bash
cd /home/donbr/open-biosciences/open-biosciences-plugins-connector-research
git status --porcelain                                   # expect clean
git diff --stat main -- . ':!docs/research/connectors' ':!docs/superpowers'
```

Expected: the second command produces **no output** — spec §11's last criterion is that no file outside `docs/research/connectors/` is created or modified.

Then walk spec §11's checklist item by item against the deliverables and confirm each.

- [ ] **Step 3: Commit**

```bash
git add docs/research/connectors/DECISION.md
git commit -m "docs(connectors): DECISION - psychology-mcp roster and interim binding

Terminal artefact of the Layer-1 discovery pass. Server roster and build
order from the five dossiers; AGE-548 q3 answered from the first-party
gateway precedent; both hci-canon producer/consumer contradictions
recorded; the interim .mcp.json delta written out but not applied; and the
capabilities that remain unsatisfiable stated plainly.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: STOP**

Spec §8 step 6: the Layer-2 build is a separate SpecKit program, and applying the interim binding is a separate PR against AGE-552. Report to the maintainer and stop. Do not create `psychology-mcp` source, do not apply the delta.

---

## Post-plan

Once `DECISION.md` is approved, three separate pieces of work follow, none of them in this plan:

1. **The interim `.mcp.json` delta** — a PR against AGE-552 applying §7.4.
2. **The Layer-2 SpecKit program** — initialise `psychology-mcp` at `/home/donbr/open-biosciences/psychology-mcp`, register it in `open-biosciences.code-workspace` and the platform README table, then one `/speckit.specify` per server from the §7.1 roster.
3. **`bio-research` adoption** of the literature envelope where it overlaps (PubMed, bioRxiv), under AGE-554.
