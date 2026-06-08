"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Cài đặt:
    pip install markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON, JSONL)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import json
from pathlib import Path

from markitdown import MarkItDown

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"

NEWS_EXTENSIONS = {".json", ".jsonl"}


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()

    for filepath in sorted(legal_dir.iterdir()):
        if filepath.suffix.lower() not in (".pdf", ".docx", ".doc"):
            continue

        print(f"Converting: {filepath.name}")
        result = md.convert(str(filepath))
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(result.text_content, encoding="utf-8")
        print(f"  ✓ Saved: {output_path}")


def _load_news_records(filepath: Path) -> list[dict]:
    """Đọc bài báo từ file JSON (1 object hoặc array) hoặc JSONL (1 object/dòng)."""
    text = filepath.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if filepath.suffix.lower() == ".jsonl":
        records = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records

    data = json.loads(text)
    if isinstance(data, list):
        return data
    return [data]


def _first_value(data: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if value:
            return str(value)
    return default


def _format_news_header(data: dict) -> str:
    title = _first_value(data, "title", "headline", default="Unknown")
    url = _first_value(data, "url", "source_url", "link", default="N/A")
    author = _first_value(data, "author", "byline")
    published = _first_value(data, "publishedAt", "published_at", "date")
    crawled = _first_value(
        data,
        "date_crawled",
        "scrapedAt",
        "scraped_at",
        "crawled_at",
        default="N/A",
    )

    header = f"# {title}\n\n"
    header += f"**Source:** {url}\n"
    if author:
        header += f"**Author:** {author}\n"
    if published:
        header += f"**Published:** {published}\n"
    header += f"**Crawled:** {crawled}\n\n---\n\n"
    return header


def _build_article_body(data: dict) -> str:
    """Lấy nội dung bài báo từ nhiều schema crawl (Crawl4AI, VTC News, ...)."""
    markdown = _first_value(data, "content_markdown", "markdown")
    if markdown:
        return markdown.strip()

    parts: list[str] = []
    sapo = _first_value(data, "sapo", "summary", "description")
    if sapo:
        parts.append(f"> {sapo}")

    paragraphs = data.get("paragraphs")
    if isinstance(paragraphs, list):
        body = "\n\n".join(str(p).strip() for p in paragraphs if str(p).strip())
        if body:
            parts.append(body)
            return "\n\n".join(parts)

    plain = _first_value(data, "contentText", "content", "text", "body")
    if plain:
        parts.append(plain.strip())

    return "\n\n".join(parts)


def _output_stem(filepath: Path, data: dict, index: int, multi_record: bool) -> str:
    article_id = _first_value(data, "articleId", "id")
    if not multi_record:
        return filepath.stem
    if article_id:
        return f"{filepath.stem}_{article_id}"
    return f"{filepath.stem}_{index:03d}"


def convert_news_articles():
    """Convert JSON/JSONL crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in sorted(news_dir.iterdir()):
        if filepath.suffix.lower() not in NEWS_EXTENSIONS:
            continue

        print(f"Converting: {filepath.name}")
        records = _load_news_records(filepath)
        multi_record = len(records) > 1

        for i, data in enumerate(records, start=1):
            body = _build_article_body(data)
            if not body:
                print(f"  ⚠ No content found in record {i}, skipping")
                continue

            stem = _output_stem(filepath, data, i, multi_record)
            output_path = output_dir / f"{stem}.md"
            content = _format_news_header(data) + body
            output_path.write_text(content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path}")


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\n✓ Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
