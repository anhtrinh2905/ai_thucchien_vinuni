# Corruption Comparison Report

## Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| Retrieval hit rate | 1.000 | 0.875 | 1.000 |
| Mean token F1 | 0.990 | 0.840 | 0.990 |
| Judge accuracy | 1.000 | 0.844 | 1.000 |
| Mean judge score | 4.938 | 4.312 | 4.938 |

## Data Quality

### Corrupted
- Passed checks: 4
- Failed checks: 2
- Overall success: False
- [PASS] row_count_minimum: Found 23 rows; expected at least 4.
- [PASS] paper_id_not_null: Null paper_id rows: 0.
- [PASS] paper_id_unique: Unique paper_id count: 23 / 23.
- [PASS] title_not_null: Null title rows: 0.
- [FAIL] summary_length: Rows with summary shorter than 40 chars: 3.
- [FAIL] freshness_threshold: Rows older than 180 days: 4.

### Repaired
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

### Corrupted
- Latest published: 2026-05-06
- Oldest published: 2010-01-01
- Stale rows: 4
- Total rows: 23
- Is fresh: False

### Repaired
- Latest published: 2026-06-02
- Oldest published: 2025-12-19
- Stale rows: 0
- Total rows: 23
- Is fresh: True

## Conclusion
Corrupted data reduced agent performance, while repair restored metrics closer to the baseline.
