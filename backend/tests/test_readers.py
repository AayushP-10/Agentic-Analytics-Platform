from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.services.readers import (
    CSVReader,
    ExcelReader,
    JSONLReader,
    JSONReader,
    ParquetReader,
    SQLiteReader,
    TSVReader,
)


@pytest.mark.parametrize(
    ("reader", "sample_key", "expected_column"),
    [
        (CSVReader(), "csv", "customer_id"),
        (TSVReader(), "tsv", "order_id"),
        (ExcelReader(), "excel", "warehouse"),
        (JSONReader(), "json", "customer_id"),
        (JSONLReader(), "jsonl", "ticket_id"),
        (ParquetReader(), "parquet", "product_id"),
    ],
)
def test_flat_file_readers_inspect_sample_files(
    generated_sample_paths: dict[str, Path],
    reader,
    sample_key: str,
    expected_column: str,
) -> None:
    sample_path = generated_sample_paths[sample_key]

    assert reader.can_read(sample_path)
    schema = reader.get_schema(sample_path)
    rows = reader.load_sample(sample_path, limit=2)

    assert expected_column in schema
    assert rows
    assert expected_column in rows[0]
    assert reader.get_row_count(sample_path) is not None


def test_sqlite_reader_lists_tables_and_samples_default_table(
    generated_sample_paths: dict[str, Path],
) -> None:
    reader = SQLiteReader()
    sqlite_path = generated_sample_paths["sqlite"]

    schema = reader.get_schema(sqlite_path)
    rows = reader.load_sample(sqlite_path, limit=2)

    assert reader.list_tables(sqlite_path) == ["customers", "orders", "products"]
    assert schema["default_table"] == "customers"
    assert "customers" in schema["tables"]
    assert rows
    assert "customer_id" in rows[0]


def test_parquet_reader_inspects_products_file(generated_sample_paths: dict[str, Path]) -> None:
    reader = ParquetReader()
    parquet_path = generated_sample_paths["parquet"]

    schema = reader.get_schema(parquet_path)

    assert "product_id" in schema
    assert "list_price" in schema
    assert reader.get_row_count(parquet_path) == 4
