from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.services.readers.base import DataReader, DataReaderError


class CSVReader(DataReader):
    supported_extensions = {".csv"}
    format_name = "csv"
    separator = ","

    def load_sample(self, file_path: Path, limit: int = 100) -> list[dict[str, Any]]:
        try:
            frame = pd.read_csv(file_path, sep=self.separator, nrows=limit)
            return self.dataframe_records(frame)
        except Exception as exc:
            raise DataReaderError(f"Could not load sample from {file_path.name}: {exc}") from exc

    def get_schema(self, file_path: Path) -> dict[str, Any]:
        try:
            frame = pd.read_csv(file_path, sep=self.separator, nrows=100)
            return self.dataframe_schema(frame)
        except Exception as exc:
            raise DataReaderError(f"Could not infer schema for {file_path.name}: {exc}") from exc

    def get_row_count(self, file_path: Path) -> int | None:
        try:
            chunks = pd.read_csv(file_path, sep=self.separator, chunksize=100_000)
            return sum(len(chunk) for chunk in chunks)
        except Exception as exc:
            raise DataReaderError(f"Could not count rows for {file_path.name}: {exc}") from exc
