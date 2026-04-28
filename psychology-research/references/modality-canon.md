# Modality Canon

Modality-specific source canon. Read on-demand by the LLM at the evidence-builder's LOCATE step to identify a claim's paradigm and select preferred sources. Failure mode is degraded quality (paradigm-mismatched results), not a safety violation.

If the LLM identifies a primary modality during a query and that modality has no entry below, emit the Tier-1b banner per spec §9 and proceed with general defaults.

## Schema

Each entry has the following fields:

``` yaml
modality: <canonical name>
abbreviations: [<list of common abbreviations>]
status: full | partial | sketch
founders: [<author names>]
modality_institutes: [<institutional bodies>]
canonical_texts:
  - title: <book or paper title>
    author: <author>
    year: <year>
    type: book | journal_article | manual | grey_literature
    notes: <one line>
preferred_journals: [<journal names>]
preferred_databases: [<pubmed | semantic-scholar | modality-institute | book-canon | other>]
paradigm_notes: <one paragraph on what kind of literature counts and what doesn't>
limits: <one paragraph on what claims this canon does not authorize>
```

`status` values:
- `full`: schema completely populated; canon load-bearing for this modality
- `partial`: schema has gaps explicitly named; useful but not authoritative
- `sketch`: skeleton only, not load-bearing; flagged for expansion

## Entries

### AEDP (Accelerated Experiential Dynamic Psychotherapy)

``` yaml
modality: AEDP (Accelerated Experiential Dynamic Psychotherapy)
abbreviations: [AEDP]
status: full
founders: [Diana Fosha]
modality_institutes:
  - AEDP Institute (aedpinstitute.org)
canonical_texts:
  - title: The Transforming Power of Affect
    author: Diana Fosha
    year: 2000
    type: book
    notes: Foundational theoretical text introducing AEDP.
  - title: The Healing Power of Emotion
    author: Diana Fosha; Daniel J. Siegel; Marion F. Solomon (eds.)
    year: 2009
    type: book
    notes: Edited volume; positions AEDP within affective neuroscience and attachment.
  - title: Undoing Aloneness and the Transformation of Suffering Into Flourishing
    author: Diana Fosha (ed.)
    year: 2021
    type: book
    notes: Recent volume on AEDP clinical principles and case material.
preferred_journals:
  - Journal of Psychotherapy Integration
  - Psychotherapy (APA Division 29)
  - Transformance (AEDP Institute internal journal)
preferred_databases: [book-canon, modality-institute, semantic-scholar, pubmed]
paradigm_notes: |
  AEDP's authoritative literature is concentrated in books, AEDP Institute publications,
  and integrative-psychotherapy journals — not primarily in PubMed-indexed RCTs. PubMed
  retrieves some AEDP-related affective-neuroscience research and case studies, but
  PubMed-only retrieval will miss the core theoretical canon. Always consult book-canon
  and modality-institute first; treat PubMed results as supplementary on AEDP-theoretical
  questions.
limits: |
  This canon authorizes claims about AEDP theory, technique, and the founder's
  positioning of the modality. It does not authorize claims about clinical efficacy
  in specific populations beyond what the canonical texts themselves claim;
  population-specific efficacy claims need additional empirical sources.
```

### IFS (Internal Family Systems)

``` yaml
modality: Internal Family Systems
abbreviations: [IFS]
status: partial
founders: [Richard C. Schwartz]
modality_institutes:
  - IFS Institute (selfleadership.org)
canonical_texts:
  - title: Internal Family Systems Therapy (2nd ed.)
    author: Richard C. Schwartz; Martha Sweezy
    year: 2020
    type: book
    notes: Updated foundational text; primary clinical reference.
  - title: No Bad Parts
    author: Richard C. Schwartz
    year: 2021
    type: book
    notes: Accessible introduction; practitioner and lay audience.
preferred_journals:
  - Journal of Marital and Family Therapy
  - Journal of Psychotherapy Integration
preferred_databases: [book-canon, modality-institute, pubmed, semantic-scholar]
paradigm_notes: |
  IFS canon is book-heavy with growing empirical research presence. Hodgdon et al.
  efficacy studies and Shadick et al. (rheumatoid arthritis) are PubMed-indexed.
  Faculty at IFS Institute and IFS-trained therapists publish clinical case material
  in integration journals. Treat book-canon as primary; supplement with PubMed for
  efficacy-claim support.
limits: |
  PARTIAL ENTRY. Schema fields populated but the preferred_journals list is
  incomplete; faculty contributors beyond Schwartz and Sweezy not yet enumerated;
  international IFS bodies not represented. Treat IFS-specific claims as supported
  rather than authoritative until this entry is upgraded to status: full.
```

## Tier-1a EFT schema-validation result

The Emotionally Focused Therapy schema-validation sketch was performed during Tier-1a to test the schema against a modality with substantial PubMed-indexed RCT presence. Result: [TO BE FILLED IN BY TASK 5 — schema validates cleanly OR schema reworks here].
