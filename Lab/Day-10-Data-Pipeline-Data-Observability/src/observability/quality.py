from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json


def _check_result(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"check": name, "passed": passed, "detail": detail}


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    row_count = len(df)
    checks.append(
        _check_result(
            "row_count_minimum",
            row_count >= 4,
            f"Found {row_count} rows; expected at least 4.",
        )
    )

    paper_id_nulls = int(df["paper_id"].isna().sum()) if "paper_id" in df.columns else row_count
    unique_paper_ids = int(df["paper_id"].nunique()) if "paper_id" in df.columns else 0
    checks.append(
        _check_result(
            "paper_id_not_null",
            paper_id_nulls == 0,
            f"Null paper_id rows: {paper_id_nulls}.",
        )
    )
    checks.append(
        _check_result(
            "paper_id_unique",
            unique_paper_ids == row_count,
            f"Unique paper_id count: {unique_paper_ids} / {row_count}.",
        )
    )

    title_nulls = int(df["title"].isna().sum()) if "title" in df.columns else row_count
    checks.append(
        _check_result(
            "title_not_null",
            title_nulls == 0,
            f"Null title rows: {title_nulls}.",
        )
    )

    short_summaries = int((df["summary_chars"] < 40).sum()) if "summary_chars" in df.columns else row_count
    checks.append(
        _check_result(
            "summary_length",
            short_summaries == 0,
            f"Rows with summary shorter than 40 chars: {short_summaries}.",
        )
    )

    stale_rows = 0
    if "age_days" in df.columns:
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())
    checks.append(
        _check_result(
            "freshness_threshold",
            stale_rows == 0,
            f"Rows older than {settings.freshness_threshold_days} days: {stale_rows}.",
        )
    )

    report = {
        "report_name": report_name,
        "total_rows": row_count,
        "passed_checks": sum(1 for item in checks if item["passed"]),
        "failed_checks": sum(1 for item in checks if not item["passed"]),
        "success": all(item["passed"] for item in checks),
        "checks": checks,
    }
    write_json(settings.paths.quality_dir / f"{report_name}.json", report)
    return report


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    published_values = df["published"].dropna().astype(str).tolist() if "published" in df.columns else []
    latest_published = max(published_values) if published_values else None
    oldest_published = min(published_values) if published_values else None

    stale_rows = 0
    if "age_days" in df.columns:
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())

    report = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": len(df),
        "freshness_threshold_days": settings.freshness_threshold_days,
        "is_fresh": stale_rows == 0,
    }
    write_json(report_path, report)
    return report
