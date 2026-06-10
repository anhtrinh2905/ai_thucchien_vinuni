from __future__ import annotations

from typing import Any

import pandas as pd

from core.utils import write_json


MIN_DOCUMENTS = 4


def _pick_rows(df: pd.DataFrame, count: int) -> pd.DataFrame:
    if len(df) <= count:
        return df.copy()
    step = max(1, len(df) // count)
    indices = list(range(0, len(df), step))[:count]
    return df.iloc[indices].copy()


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    if len(df) < MIN_DOCUMENTS:
        raise RuntimeError(f"Need at least {MIN_DOCUMENTS} cleaned documents to build a test set.")

    selected = _pick_rows(df, min(8, len(df)))
    test_set: list[dict[str, Any]] = []
    question_id = 1

    for _, row in selected.iterrows():
        paper_id = row["paper_id"]
        title = row["title"]

        test_set.append(
            {
                "id": f"q{question_id}",
                "question_type": "summary",
                "question": f"What is the main topic of the paper '{title}'?",
                "ground_truth": row["summary"].split(".")[0].strip() + ".",
                "ground_truth_doc_ids": [paper_id],
            }
        )
        question_id += 1

        if row["authors_joined"]:
            test_set.append(
                {
                    "id": f"q{question_id}",
                    "question_type": "authors",
                    "question": f"Who authored the paper '{title}'?",
                    "ground_truth": row["authors_joined"],
                    "ground_truth_doc_ids": [paper_id],
                }
            )
            question_id += 1

        if row["published"]:
            test_set.append(
                {
                    "id": f"q{question_id}",
                    "question_type": "date",
                    "question": f"When was the paper '{title}' published?",
                    "ground_truth": row["published"],
                    "ground_truth_doc_ids": [paper_id],
                }
            )
            question_id += 1

        if row["categories_joined"]:
            test_set.append(
                {
                    "id": f"q{question_id}",
                    "question_type": "categories",
                    "question": f"What categories apply to the paper '{title}'?",
                    "ground_truth": row["categories_joined"],
                    "ground_truth_doc_ids": [paper_id],
                }
            )
            question_id += 1

    write_json(output_path, test_set)
    return test_set
