import sqlite3
from pathlib import Path

import pandas as pd

from scripts import generate_sample_data


def test_sample_data_generation_creates_expected_files(
    tmp_path: Path, monkeypatch
) -> None:
    sample_dir = tmp_path / "sample"
    sqlite_dir = tmp_path / "sqlite"
    monkeypatch.setattr(generate_sample_data, "DATA_SAMPLE_DIR", sample_dir)
    monkeypatch.setattr(generate_sample_data, "SQLITE_DIR", sqlite_dir)

    generated = generate_sample_data.generate()

    expected = {
        sample_dir / "customers.csv",
        sample_dir / "orders.csv",
        sample_dir / "products.parquet",
        sample_dir / "support_tickets.jsonl",
        sample_dir / "inventory.xlsx",
        sqlite_dir / "company.db",
    }
    assert set(generated) == expected
    assert all(path.exists() for path in expected)


def test_generated_csv_files_have_expected_columns(tmp_path: Path, monkeypatch) -> None:
    sample_dir = tmp_path / "sample"
    sqlite_dir = tmp_path / "sqlite"
    monkeypatch.setattr(generate_sample_data, "DATA_SAMPLE_DIR", sample_dir)
    monkeypatch.setattr(generate_sample_data, "SQLITE_DIR", sqlite_dir)
    generate_sample_data.generate()

    customers = pd.read_csv(sample_dir / "customers.csv")
    orders = pd.read_csv(sample_dir / "orders.csv")

    assert customers.columns.tolist() == [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "signup_date",
        "region",
        "customer_segment",
        "lifetime_value",
        "churn_risk_score",
    ]
    assert orders.columns.tolist() == [
        "order_id",
        "customer_id",
        "order_date",
        "product_id",
        "quantity",
        "unit_price",
        "discount",
        "order_status",
        "sales_channel",
    ]


def test_generated_parquet_and_sqlite_can_be_read(tmp_path: Path, monkeypatch) -> None:
    sample_dir = tmp_path / "sample"
    sqlite_dir = tmp_path / "sqlite"
    monkeypatch.setattr(generate_sample_data, "DATA_SAMPLE_DIR", sample_dir)
    monkeypatch.setattr(generate_sample_data, "SQLITE_DIR", sqlite_dir)
    generate_sample_data.generate()

    products = pd.read_parquet(sample_dir / "products.parquet")
    assert products.columns.tolist() == [
        "product_id",
        "product_name",
        "category",
        "cost",
        "list_price",
        "supplier",
        "active_flag",
    ]

    with sqlite3.connect(sqlite_dir / "company.db") as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name",
            connection,
        )

    assert tables["name"].tolist() == ["customers", "orders", "products"]
