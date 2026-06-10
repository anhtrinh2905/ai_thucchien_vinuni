from __future__ import annotations

import pandas as pd

from core.utils import compact_join, normalize_whitespace, write_json


def _rebuild_text_for_embedding(row: pd.Series) -> str:
    return (
        f"Title: {row['title']}\n"
        f"Authors: {row['authors_joined']}\n"
        f"Categories: {row['categories_joined']}\n"
        f"Published: {row['published']}\n"
        f"Summary: {row['summary']}"
    )


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    corrupted = df.copy()
    log: list[dict] = []

    drop_count = min(2, max(1, len(corrupted) // 6))
    drop_indices = corrupted.sort_values("published", ascending=False).head(drop_count).index.tolist()
    corrupted = corrupted.drop(index=drop_indices).reset_index(drop=True)
    log.append({"action": "drop_latest_records", "count": drop_count, "indices": drop_indices})

    blank_indices = corrupted.sample(n=min(2, len(corrupted)), random_state=42).index.tolist()
    for idx in blank_indices:
        corrupted.at[idx, "summary"] = ""
        corrupted.at[idx, "summary_chars"] = 0
    log.append({"action": "blank_summary", "indices": blank_indices})

    noise_indices = corrupted.index[: min(3, len(corrupted))].tolist()
    for idx in noise_indices:
        corrupted.at[idx, "summary"] = normalize_whitespace(
            f"{corrupted.at[idx, 'summary']} NOISE TOKEN xyz123 corrupted text."
        )
        corrupted.at[idx, "summary_chars"] = len(corrupted.at[idx, "summary"])
    log.append({"action": "inject_noise", "indices": noise_indices})

    truncate_indices = corrupted.index[-min(2, len(corrupted)) :].tolist()
    for idx in truncate_indices:
        corrupted.at[idx, "title"] = corrupted.at[idx, "title"][:20].strip()
    log.append({"action": "truncate_title", "indices": truncate_indices})

    stale_indices = corrupted.index[: min(2, len(corrupted))].tolist()
    for idx in stale_indices:
        corrupted.at[idx, "published"] = "2010-01-01"
        corrupted.at[idx, "age_days"] = 5000
    log.append({"action": "stale_publication_date", "indices": stale_indices})

    duplicate_rows = corrupted.head(min(2, len(corrupted))).copy()
    duplicate_rows["paper_id"] = duplicate_rows["paper_id"].apply(lambda value: f"{value}-dup")
    corrupted = pd.concat([corrupted, duplicate_rows], ignore_index=True)
    log.append({"action": "add_duplicates", "count": len(duplicate_rows)})

    corrupted["text_for_embedding"] = corrupted.apply(_rebuild_text_for_embedding, axis=1)
    corrupted["authors_joined"] = corrupted["authors"].apply(
        lambda authors: compact_join(authors if isinstance(authors, list) else [])
    )
    corrupted["categories_joined"] = corrupted["categories"].apply(
        lambda categories: compact_join(categories if isinstance(categories, list) else [])
    )

    write_json(output_log_path, {"seed": 42, "actions": log, "rows_before": len(df), "rows_after": len(corrupted)})
    return corrupted
