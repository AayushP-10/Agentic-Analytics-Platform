from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.services.data_intake_service import (
    DataIntakeService,
    UnsupportedFileTypeError,
)


def test_data_intake_service_returns_standard_metadata(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )

    metadata = service.inspect_file(generated_sample_paths["csv"], sample_limit=3)

    assert metadata.asset_id
    assert metadata.file_name == "customers.csv"
    assert metadata.file_extension == ".csv"
    assert metadata.file_size_bytes > 0
    assert metadata.format == "csv"
    assert metadata.row_count == 7
    assert metadata.column_count == 9
    assert "customer_id" in metadata.columns
    assert "customer_id" in metadata.data_schema
    assert len(metadata.sample_rows) == 3
    assert metadata.created_at is not None


def test_unsupported_file_type_raises_clear_error(tmp_path: Path) -> None:
    service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )
    unsupported = tmp_path / "notes.txt"
    unsupported.write_text("not supported", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError, match="Unsupported file type"):
        service.inspect_file(unsupported)


def test_service_persists_and_fetches_metadata(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )

    metadata = service.inspect_file(generated_sample_paths["parquet"])
    fetched = service.get_asset(metadata.asset_id)

    assert fetched.asset_id == metadata.asset_id
    assert fetched.format == "parquet"
    assert fetched.row_count == 4
