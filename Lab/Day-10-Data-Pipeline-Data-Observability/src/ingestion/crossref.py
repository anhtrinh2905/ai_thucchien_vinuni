from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import time

import requests

from core.config import Settings
from core.utils import normalize_whitespace, write_json


CROSSREF_API_URL = "https://api.crossref.org/works"


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    return normalize_whitespace(cleaned)


def _parse_authors(item: dict) -> list[str]:
    authors: list[str] = []
    for author in item.get("author", []):
        given = author.get("given", "")
        family = author.get("family", "")
        name = normalize_whitespace(f"{given} {family}")
        if name:
            authors.append(name)
    return authors


def _parse_date(parts: dict | None) -> str:
    if not parts:
        return ""
    year = parts.get("date-parts", [[None]])[0][0]
    month = parts.get("date-parts", [[None, None]])[0][1] if len(parts.get("date-parts", [[]])[0]) > 1 else None
    day = parts.get("date-parts", [[None, None, None]])[0][2] if len(parts.get("date-parts", [[]])[0]) > 2 else None
    if not year:
        return ""
    if month and day:
        return f"{year:04d}-{month:02d}-{day:02d}"
    if month:
        return f"{year:04d}-{month:02d}"
    return f"{year:04d}"


def _pick_published(item: dict) -> str:
    for key in ("published-print", "published-online", "issued", "created"):
        value = _parse_date(item.get(key))
        if value:
            return value
    return ""


def _pick_updated(item: dict) -> str:
    for key in ("updated", "deposited", "indexed"):
        value = _parse_date(item.get(key))
        if value:
            return value
    return _pick_published(item)


def _pick_pdf_url(item: dict) -> str:
    for link in item.get("link", []):
        if link.get("content-type") == "application/pdf" and link.get("URL"):
            return link["URL"]
    return ""


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        doi = item.get("DOI", "").strip().lower()
        title_list = item.get("title") or []
        title = normalize_whitespace(title_list[0]) if title_list else ""
        summary = _strip_html(item.get("abstract", ""))
        authors = _parse_authors(item)
        categories = [normalize_whitespace(value) for value in item.get("subject", []) if value]
        primary_category = categories[0] if categories else "uncategorized"
        published = _pick_published(item)
        updated = _pick_updated(item)
        abs_url = f"https://doi.org/{doi}" if doi else ""
        pdf_url = _pick_pdf_url(item)
        comment = normalize_whitespace(item.get("note", ""))

        if not doi or not title or not summary:
            continue

        records.append(
            PaperRecord(
                paper_id=doi,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def _fetch_with_retry(url: str, params: dict, max_retries: int = 3) -> dict:
    headers = {"User-Agent": "day10-lab/0.1 (mailto:student@example.com)"}
    for attempt in range(max_retries):
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code in {429, 503} and attempt < max_retries - 1:
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Failed to fetch Crossref data after retries.")


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    payload = _fetch_with_retry(CROSSREF_API_URL, params)

    write_json(settings.paths.raw_api_response, payload)
    records = parse_crossref_payload(payload)
    write_json(settings.paths.raw_records_json, [asdict(record) for record in records])
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    from core.utils import read_json

    payload = read_json(path)
    return [PaperRecord(**item) for item in payload]
