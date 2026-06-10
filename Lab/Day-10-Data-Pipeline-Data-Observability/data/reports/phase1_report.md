# Phase 1 Baseline Report

## Source Summary
- Source API: Crossref REST API
- Query: agentic retrieval augmented generation large language model
- Filter: from-pub-date:2025-12-12,has-abstract:true
- Raw records: 23
- Clean records: 23

## Evaluation Metrics
- Samples: 32
- Retrieval hit rate: 1.000
- Mean token F1: 0.990
- Judge accuracy: 1.000
- Mean judge score: 4.938
- Ragas: {'skipped': 'Set RUN_RAGAS=1 to enable the slower Ragas pass.'}

## Data Quality
- Passed checks: 6
- Failed checks: 0
- Overall success: True
- [PASS] row_count_minimum: Found 23 rows; expected at least 4.
- [PASS] paper_id_not_null: Null paper_id rows: 0.
- [PASS] paper_id_unique: Unique paper_id count: 23 / 23.
- [PASS] title_not_null: Null title rows: 0.
- [PASS] summary_length: Rows with summary shorter than 40 chars: 0.
- [PASS] freshness_threshold: Rows older than 180 days: 0.

## Freshness
- Latest published: 2026-06-02
- Oldest published: 2025-12-19
- Stale rows: 0
- Total rows: 23
- Is fresh: True
