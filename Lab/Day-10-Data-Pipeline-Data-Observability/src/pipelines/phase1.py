from __future__ import annotations

from core.config import load_settings
from core.utils import now_utc, read_json, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.agent import build_agent, run_agent_question
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    settings = load_settings()

    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        records = fetch_source_records(settings)
    else:
        records = load_raw_records(settings.paths.raw_records_json)

    clean_df = build_clean_dataframe(records, run_date=now_utc())
    if clean_df.empty:
        raise RuntimeError("Cleaning produced an empty dataframe.")

    write_csv(clean_df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, clean_df.to_dict(orient="records"))

    index = LocalEmbeddingIndex.build(clean_df, settings=settings, embeddings_output_path=settings.paths.embeddings_json)

    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        build_test_set(clean_df, settings.paths.eval_testset)
    else:
        read_json(settings.paths.eval_testset)

    metrics_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )

    quality = run_data_quality_checks(clean_df, settings=settings, report_name="baseline_quality")
    freshness = build_freshness_report(clean_df, settings=settings, report_path=settings.paths.freshness_report)

    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "source_filter": settings.source_filter,
        "raw_records": len(records),
        "clean_records": len(clean_df),
    }
    generate_phase1_report(
        settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=metrics_bundle.summary,
        quality=quality,
        freshness=freshness,
    )

    agent = build_agent(settings, index)
    demo_questions = read_json(settings.paths.eval_testset)[:2]
    demo_answers = [
        {"question": item["question"], "answer": run_agent_question(agent, item["question"])}
        for item in demo_questions
    ]
    write_json(settings.paths.demo_answers, demo_answers)

    print(f"Baseline pipeline complete. Clean rows: {len(clean_df)}")
    print(f"Metrics saved to: {settings.paths.baseline_metrics}")
    print(f"Report saved to: {settings.paths.baseline_report}")
