from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.services.readers.base import DataReader, DataReaderError


class JSONReader(DataReader):
    supported_extensions = {".json"}
    format_name = "json"

    def load_sample(self, file_path: Path, limit: int = 100) -> list[dict[str, Any]]:
        try:
            frame = self._read_frame(file_path).head(limit)
            return self.dataframe_records(frame)
        except Exception as exc:
            raise DataReaderError(f"Could not load sample from {file_path.name}: {exc}") from exc

    def get_schema(self, file_path: Path) -> dict[str, Any]:
        try:
            frame = self._read_frame(file_path).head(100)
            return self.dataframe_schema(frame)
        except Exception as exc:
            raise DataReaderError(f"Could not infer schema for {file_path.name}: {exc}") from exc

    def get_row_count(self, file_path: Path) -> int | None:
        try:
            return len(self._read_frame(file_path))
        except Exception as exc:
            raise DataReaderError(f"Could not count rows for {file_path.name}: {exc}") from exc

    def _read_frame(self, file_path: Path) -> pd.DataFrame:
        with file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if isinstance(payload, dict):
            records = payload.get("records", payload.get("data", payload))
        else:
            records = payload
        return pd.json_normalize(records)


class JSONLReader(DataReader):
    supported_extensions = {".jsonl", ".ndjson"}
    format_name = "jsonl"

    def load_sample(self, file_path: Path, limit: int = 100) -> list[dict[str, Any]]:
        try:
            frame = pd.read_json(file_path, lines=True, nrows=limit)
            return self.dataframe_records(frame)
        except Exception as exc:
            raise DataReaderError(f"Could not load sample from {file_path.name}: {exc}") from exc

    def get_schema(self, file_path: Path) -> dict[str, Any]:
        try:
            frame = pd.read_json(file_path, lines=True, nrows=100)
            return self.dataframe_schema(frame)
        except Exception as exc:
            raise DataReaderError(f"Could not infer schema for {file_path.name}: {exc}") from exc

    def get_row_count(self, file_path: Path) -> int | None:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                return sum(1 for line in file if line.strip())
        except Exception as exc:
            raise DataReaderError(f"Could not count rows for {file_path.name}: {exc}") from exc
