from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.app.services.data_intake_service import DataIntakeService
from backend.app.services.profiling_service import ProfilingService


def make_service(tmp_path: Path) -> ProfilingService:
    intake_service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )
    return ProfilingService(
        intake_service=intake_service,
        reports_dir=tmp_path / "reports" / "profiles",
    )


def column(profile, name: str):
    return next(item for item in profile.columns if item.column_name == name)


def test_profiles_customers_csv_and_detects_missing_duplicates_and_identifiers(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["csv"])

    assert profile.file_name == "customers.csv"
    assert profile.format == "csv"
    assert profile.row_count == 7
    assert profile.column_count == 9
    assert profile.duplicate_row_count == 0
    assert profile.missing_cell_count > 0
    assert "email" in profile.quality_summary.columns_with_missing_values
    assert "customer_id" in profile.quality_summary.suspected_identifier_columns
    assert "signup_date" in profile.quality_summary.suspected_datetime_columns
    assert Path(profile.report_path).exists()


def test_profiles_orders_csv_and_detects_duplicate_rows_and_negative_values(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["csv"].with_name("orders.csv"))
    quantity = column(profile, "quantity")

    assert profile.duplicate_row_count == 1
    assert profile.quality_summary.duplicate_rows_detected is True
    assert quantity.numeric_profile is not None
    assert quantity.numeric_profile.negative_count == 1
    assert any(w.warning_type == "negative_values" for w in quantity.warnings)


def test_profiles_products_parquet(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["parquet"])

    assert profile.format == "parquet"
    assert profile.row_count == 4
    assert "list_price" in profile.quality_summary.suspected_currency_or_amount_columns


def test_profiles_support_tickets_jsonl(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["jsonl"])

    assert profile.format == "jsonl"
    assert profile.row_count == 4
    assert "satisfaction_score" in profile.quality_summary.columns_with_missing_values


def test_profiles_inventory_excel_and_detects_negative_stock(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["excel"])
    stock = column(profile, "stock_on_hand")

    assert profile.format == "excel"
    assert stock.numeric_profile is not None
    assert stock.numeric_profile.negative_count == 1


def test_profiles_sqlite_selected_table(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["sqlite"], table_name="orders")

    assert profile.format == "sqlite"
    assert profile.table_name == "orders"
    assert profile.row_count == 5
    assert "order_id" in [item.column_name for item in profile.columns]


def test_detects_high_cardinality_column(tmp_path: Path) -> None:
    path = tmp_path / "high_cardinality.csv"
    pd.DataFrame({"record_id": [f"R{i:03d}" for i in range(20)], "value": range(20)}).to_csv(
        path, index=False
    )
    service = make_service(tmp_path)

    profile = service.profile_file(path)

    assert "record_id" in profile.quality_summary.columns_with_high_cardinality
    assert "record_id" in profile.quality_summary.suspected_identifier_columns


def test_saves_and_loads_profile_report(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = make_service(tmp_path)

    profile = service.profile_file(generated_sample_paths["parquet"])
    loaded = service.get_report(profile.profile_id)

    assert loaded.profile_id == profile.profile_id
    assert loaded.file_name == "products.parquet"
