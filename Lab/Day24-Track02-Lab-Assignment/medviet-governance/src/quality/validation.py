# src/quality/validation.py
import great_expectations as gx
import pandas as pd
from great_expectations.core.expectation_suite import ExpectationSuite


def build_patient_expectation_suite() -> ExpectationSuite:
    context = gx.get_context()
    suite = context.add_expectation_suite("patient_data_suite")

    df = pd.read_csv("data/raw/patients_raw.csv")
    validator = context.sources.pandas_default.read_dataframe(df)

    validator.expect_column_values_to_not_be_null("patient_id")

    validator.expect_column_value_lengths_to_equal(column="cccd", value=12)

    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem", min_value=0, max_value=50
    )

    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh", value_set=valid_conditions
    )

    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    )

    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    original_df = pd.read_csv("data/raw/patients_raw.csv")
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
    }

    original_cccds = set(original_df["cccd"].astype(str))
    anon_cccds = set(df["cccd"].astype(str))
    overlap = original_cccds & anon_cccds
    if overlap:
        results["success"] = False
        results["failed_checks"].append(
            f"Original CCCD values still present: {len(overlap)}"
        )

    important_cols = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    for col in important_cols:
        if df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values in {col}")

    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append("Row count mismatch")

    return results
