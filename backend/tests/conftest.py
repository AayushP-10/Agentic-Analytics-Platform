from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts import generate_sample_data


@pytest.fixture
def generated_sample_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    sample_dir = tmp_path / "sample"
    sqlite_dir = tmp_path / "sqlite"
    monkeypatch.setattr(generate_sample_data, "DATA_SAMPLE_DIR", sample_dir)
    monkeypatch.setattr(generate_sample_data, "SQLITE_DIR", sqlite_dir)
    generate_sample_data.generate()

    orders = pd.read_csv(sample_dir / "orders.csv")
    orders.to_csv(sample_dir / "orders.tsv", sep="\t", index=False)

    customers = pd.read_csv(sample_dir / "customers.csv")
    customers.to_json(sample_dir / "customers.json", orient="records", indent=2)

    return {
        "csv": sample_dir / "customers.csv",
        "tsv": sample_dir / "orders.tsv",
        "excel": sample_dir / "inventory.xlsx",
        "json": sample_dir / "customers.json",
        "jsonl": sample_dir / "support_tickets.jsonl",
        "parquet": sample_dir / "products.parquet",
        "sqlite": sqlite_dir / "company.db",
    }
