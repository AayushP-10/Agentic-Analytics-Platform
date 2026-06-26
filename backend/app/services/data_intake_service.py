from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from backend.app.core.settings import (
    INTAKE_METADATA_PATH,
    MAX_UPLOAD_SIZE_BYTES,
    RAW_DATA_DIR,
    SUPPORTED_EXTENSIONS,
)
from backend.app.schemas.intake import DataAssetMetadata
from backend.app.services.readers import (
    CSVReader,
    ExcelReader,
    JSONLReader,
    JSONReader,
    ParquetReader,
    SQLiteReader,
    TSVReader,
)
from backend.app.services.readers.base import DataReader


class UnsupportedFileTypeError(ValueError):
    pass


class IntakeFileError(ValueError):
    pass


class DataIntakeService:
    def __init__(
        self,
        raw_data_dir: Path = RAW_DATA_DIR,
        metadata_path: Path = INTAKE_METADATA_PATH,
        max_upload_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
        readers: list[DataReader] | None = None,
    ) -> None:
        self.raw_data_dir = raw_data_dir
        self.metadata_path = metadata_path
        self.max_upload_size_bytes = max_upload_size_bytes
        self.readers = readers or [
            CSVReader(),
            TSVReader(),
            ExcelReader(),
            JSONReader(),
            JSONLReader(),
            ParquetReader(),
            SQLiteReader(),
        ]

    def inspect_file(self, file_path: Path, sample_limit: int = 100) -> DataAssetMetadata:
        resolved_path = file_path.resolve()
        self._validate_supported_extension(resolved_path)
        if not resolved_path.exists() or not resolved_path.is_file():
            raise IntakeFileError(f"File does not exist: {file_path}")

        reader = self._reader_for(resolved_path)
        schema = reader.get_schema(resolved_path)
        sample_rows = reader.load_sample(resolved_path, limit=sample_limit)
        row_count = reader.get_row_count(resolved_path)
        columns = self._columns_from_schema(schema)

        metadata = DataAssetMetadata(
            asset_id=self._asset_id(resolved_path),
            file_name=resolved_path.name,
            file_path=str(resolved_path),
            file_extension=resolved_path.suffix.lower(),
            file_size_bytes=resolved_path.stat().st_size,
            format=reader.format_name,
            row_count=row_count,
            column_count=len(columns) if columns else None,
            columns=columns,
            data_schema=schema,
            sample_rows=sample_rows,
            warnings=[],
            created_at=datetime.now(UTC),
        )
        self.save_metadata(metadata)
        return metadata

    def save_upload(self, filename: str, file_object: BinaryIO) -> Path:
        safe_name = self.sanitize_filename(filename)
        destination = self.raw_data_dir / safe_name
        destination = self._deduplicate_destination(destination)
        self._validate_supported_extension(destination)

        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        bytes_written = 0
        with destination.open("wb") as output:
            while chunk := file_object.read(1024 * 1024):
                bytes_written += len(chunk)
                if bytes_written > self.max_upload_size_bytes:
                    output.close()
                    destination.unlink(missing_ok=True)
                    raise IntakeFileError(
                        f"File exceeds maximum upload size of {self.max_upload_size_bytes} bytes"
                    )
                output.write(chunk)
        return destination

    def list_assets(self) -> list[dict[str, object]]:
        persisted = self._read_metadata_store()
        if persisted:
            return list(persisted.values())

        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        assets = []
        for path in sorted(self.raw_data_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                assets.append(
                    {
                        "asset_id": self._asset_id(path.resolve()),
                        "file_name": path.name,
                        "file_path": str(path.resolve()),
                        "file_extension": path.suffix.lower(),
                        "file_size_bytes": path.stat().st_size,
                    }
                )
        return assets

    def get_asset(self, asset_id: str) -> DataAssetMetadata:
        persisted = self._read_metadata_store()
        if asset_id in persisted:
            return DataAssetMetadata.model_validate(persisted[asset_id])

        for path in self.raw_data_dir.iterdir():
            if path.is_file() and self._asset_id(path.resolve()) == asset_id:
                return self.inspect_file(path)
        raise IntakeFileError(f"Asset not found: {asset_id}")

    def save_metadata(self, metadata: DataAssetMetadata) -> None:
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        persisted = self._read_metadata_store()
        persisted[metadata.asset_id] = metadata.model_dump(mode="json", by_alias=True)
        with self.metadata_path.open("w", encoding="utf-8") as file:
            json.dump(persisted, file, indent=2)

    def sanitize_filename(self, filename: str) -> str:
        name = Path(filename).name.strip()
        name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
        name = name.strip(" .")
        if not name:
            raise IntakeFileError("Uploaded file name is empty after sanitization")
        return name

    def _reader_for(self, file_path: Path) -> DataReader:
        for reader in self.readers:
            if reader.can_read(file_path):
                return reader
        raise UnsupportedFileTypeError(f"Unsupported file type: {file_path.suffix.lower()}")

    def _validate_supported_extension(self, file_path: Path) -> None:
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise UnsupportedFileTypeError(
                f"Unsupported file type '{file_path.suffix.lower()}'. Supported: {supported}"
            )

    def _read_metadata_store(self) -> dict[str, dict[str, object]]:
        if not self.metadata_path.exists():
            return {}
        with self.metadata_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if not isinstance(payload, dict):
            return {}
        return payload

    def _deduplicate_destination(self, destination: Path) -> Path:
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = destination.suffix
        for index in range(1, 10_000):
            candidate = destination.with_name(f"{stem}_{index}{suffix}")
            if not candidate.exists():
                return candidate
        raise IntakeFileError(f"Could not create a unique filename for {destination.name}")

    def _columns_from_schema(self, schema: dict[str, object]) -> list[str]:
        if "tables" in schema:
            default_table = schema.get("default_table")
            tables = schema.get("tables")
            if isinstance(default_table, str) and isinstance(tables, dict):
                table_schema = tables.get(default_table, {})
                if isinstance(table_schema, dict):
                    return list(table_schema.keys())
            return []
        return list(schema.keys())

    def _asset_id(self, file_path: Path) -> str:
        stat = file_path.stat()
        fingerprint = f"{file_path}|{stat.st_size}|{stat.st_mtime_ns}"
        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]


def copy_file_for_tests(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
