# Classification rubric

Applied when hand-refining `probe/results/<connector>.json`. Deviating from this
is a review finding — Task 8 compares these classifications across connectors, so
five independent judgements have to be made the same way to be comparable.

Passed verbatim to every per-connector agent.

## `venue_class` — classify the TOP result only

Decide from the item's own registered metadata, never from the URL or the index
that surfaced it. An index is a lookup vehicle, not a peer-review warrant
(spec §6.1).

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

`unverified` is a legitimate, expected outcome. It is the signal that a connector
cannot support the literature envelope for that item, which is a first-order
finding, not a failure to try harder.

## `metadata_completeness` — what the API ACTUALLY returned

List only keys present and non-null **in the payload for that query**. Do not list a
key because the API documents it, and do not list a key resolved by a second lookup
to a different connector.

Registry keys: `doi` `pmid` `pmcid` `openalex_id` `semantic_scholar_id` `osf_id`
`arxiv_id` `isbn` `issn`

Envelope fields: `type` `venue` `publisher` `retraction_status` `oa_status`

`retraction_status` counts only if the API returns a retraction signal — an absent
field is not "not retracted".

## `result`

- `hit` — a top result that genuinely addresses the query
- `partial` — results returned, but the top one is tangential, wrong population,
  or wrong literature (say which in `notes`)
- `miss` — nothing addressing the query, regardless of `n_results`

**Q6 in particular:** literature about *fledgling* or newly-formed relationships is
`partial`, not `hit`. The query is scoped to established dyads precisely to preserve
that discrimination.

## C1 (positive control)

Expected `hit` for every connector. A miss means a broken client — diagnose and fix
the adapter before accepting the dossier. Do not record a C1 miss as a coverage gap,
and do not count C1 toward the connector's coverage score.

## C2 (negative control)

| Outcome | Record |
|---|---|
| Zero results | `result: miss`, `n_results: 0` |
| Non-empty, no construct match | `result: miss` plus the note `"token search returned adjacent papers; no construct match"` |
| A result presented as matching the fabricated construct or its citation | **record it in the dossier §7 as a finding**, not merely as a cell |

The failure mode under test is a confident exact match for something that does not
exist — not breadth of recall.
