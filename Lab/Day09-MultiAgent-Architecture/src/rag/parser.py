from __future__ import annotations


def parse_policy_markdown(markdown_text: str) -> list[dict]:
    chunks = []
    current_h2 = ""
    current_h3 = ""
    content_lines: list[str] = []

    def flush() -> None:
        if not current_h3 or not current_h2:
            return
        content = "\n".join(content_lines).strip()
        if not content:
            return
        h2_title = current_h2.lstrip("#").strip()
        h3_title = current_h3.lstrip("#").strip()
        rendered = f"{current_h2}\n{current_h3}\n{content}"
        chunks.append({
            "section_h2": h2_title,
            "section_h3": h3_title,
            "citation": f"policy_mock_vi.md > {h3_title}",
            "rendered_text": rendered,
        })

    for line in markdown_text.splitlines():
        if line.startswith("## "):
            flush()
            current_h2 = line.strip()
            current_h3 = ""
            content_lines = []
        elif line.startswith("### "):
            flush()
            current_h3 = line.strip()
            content_lines = []
        elif current_h3:
            content_lines.append(line)

    flush()
    return chunks
