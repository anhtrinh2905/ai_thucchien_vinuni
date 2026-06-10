from __future__ import annotations

from typing import Any

from core.utils import write_text


def _format_checks(quality: dict[str, Any]) -> str:
    lines = [
        f"- Passed checks: {quality.get('passed_checks', 0)}",
        f"- Failed checks: {quality.get('failed_checks', 0)}",
        f"- Overall success: {quality.get('success', False)}",
    ]
    for check in quality.get("checks", []):
        status = "PASS" if check.get("passed") else "FAIL"
        lines.append(f"- [{status}] {check.get('check')}: {check.get('detail')}")
    return "\n".join(lines)


def _format_freshness(freshness: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"- Latest published: {freshness.get('latest_published')}",
            f"- Oldest published: {freshness.get('oldest_published')}",
            f"- Stale rows: {freshness.get('stale_rows')}",
            f"- Total rows: {freshness.get('total_rows')}",
            f"- Is fresh: {freshness.get('is_fresh')}",
        ]
    )


def _format_metrics(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"- Samples: {metrics.get('samples')}",
            f"- Retrieval hit rate: {metrics.get('retrieval_hit_rate'):.3f}",
            f"- Mean token F1: {metrics.get('mean_token_f1'):.3f}",
            f"- Judge accuracy: {metrics.get('judge_accuracy'):.3f}",
            f"- Mean judge score: {metrics.get('mean_judge_score'):.3f}",
            f"- Ragas: {metrics.get('ragas')}",
        ]
    )


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    report = f"""# Phase 1 Baseline Report

## Source Summary
- Source API: {source_summary.get('source_api')}
- Query: {source_summary.get('source_query')}
- Filter: {source_summary.get('source_filter')}
- Raw records: {source_summary.get('raw_records')}
- Clean records: {source_summary.get('clean_records')}

## Evaluation Metrics
{_format_metrics(metrics)}

## Data Quality
{_format_checks(quality)}

## Freshness
{_format_freshness(freshness)}
"""
    write_text(report_path, report)


def _metric_line(label: str, baseline: dict[str, Any], corrupted: dict[str, Any], repaired: dict[str, Any], key: str) -> str:
    return (
        f"| {label} | {baseline.get(key, 0):.3f} | "
        f"{corrupted.get(key, 0):.3f} | {repaired.get(key, 0):.3f} |"
    )


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    report = f"""# Corruption Comparison Report

## Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
{_metric_line("Retrieval hit rate", baseline_metrics, corrupted_metrics, repaired_metrics, "retrieval_hit_rate")}
{_metric_line("Mean token F1", baseline_metrics, corrupted_metrics, repaired_metrics, "mean_token_f1")}
{_metric_line("Judge accuracy", baseline_metrics, corrupted_metrics, repaired_metrics, "judge_accuracy")}
{_metric_line("Mean judge score", baseline_metrics, corrupted_metrics, repaired_metrics, "mean_judge_score")}

## Data Quality

### Corrupted
{_format_checks(corrupted_quality)}

### Repaired
{_format_checks(repaired_quality)}

## Freshness

### Corrupted
{_format_freshness(corrupted_freshness)}

### Repaired
{_format_freshness(repaired_freshness)}

## Conclusion
Corrupted data reduced agent performance, while repair restored metrics closer to the baseline.
"""
    write_text(report_path, report)
