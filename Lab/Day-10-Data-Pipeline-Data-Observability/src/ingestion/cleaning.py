from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from core.utils import compact_join, normalize_whitespace
from ingestion.crossref import PaperRecord


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            parsed = datetime.strptime(value, fmt).replace(tzinfo=UTC)
            return parsed
        except ValueError:
            continue
    return None


def _normalize_authors(authors: list[str]) -> list[str]:
    return [normalize_whitespace(author) for author in authors if normalize_whitespace(author)]


def _normalize_categories(categories: list[str], primary_category: str) -> list[str]:
    normalized = [normalize_whitespace(category) for category in categories if normalize_whitespace(category)]
    if not normalized and primary_category:
        normalized = [normalize_whitespace(primary_category)]
    return normalized or ["uncategorized"]


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    rows: list[dict] = []
    for record in records:
        title = normalize_whitespace(record.title)
        summary = normalize_whitespace(record.summary)
        authors = _normalize_authors(record.authors)
        categories = _normalize_categories(record.categories, record.primary_category)
        published_dt = _parse_date(record.published)
        updated_dt = _parse_date(record.updated) or published_dt

        if not record.paper_id or not title or not summary or len(summary) < 40:
            continue

        age_days = (run_date - published_dt).days if published_dt else None
        authors_joined = compact_join(authors)
        categories_joined = compact_join(categories)

        rows.append(
            {
                "paper_id": record.paper_id.lower(),
                "title": title,
                "summary": summary,
                "authors": authors,
                "categories": categories,
                "primary_category": categories[0],
                "published": record.published,
                "updated": updated_dt.strftime("%Y-%m-%d") if updated_dt else record.updated,
                "age_days": age_days,
                "abs_url": record.abs_url,
                "pdf_url": record.pdf_url,
                "comment": normalize_whitespace(record.comment),
                "authors_joined": authors_joined,
                "categories_joined": categories_joined,
                "summary_chars": len(summary),
                "text_for_embedding": (
                    f"Title: {title}\n"
                    f"Authors: {authors_joined}\n"
                    f"Categories: {categories_joined}\n"
                    f"Published: {record.published}\n"
                    f"Summary: {summary}"
                ),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.drop_duplicates(subset=["paper_id"], keep="first")
    df = df.sort_values(by=["published", "title"], ascending=[False, True]).reset_index(drop=True)
    return df
