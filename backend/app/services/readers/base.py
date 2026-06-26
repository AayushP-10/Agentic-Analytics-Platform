from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class DataReaderError(RuntimeError):
    """Raised when a supported file cannot be inspected safely."""


class DataReader(ABC):
    supported_extensions: set[str] = set()
    format_name: str = "unknown"

    def can_read(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def extract_metadata(self, file_path: Path) -> dict[str, Any]:
        try:
            return {
                "format": self.format_name,
                "file_size_bytes": file_path.stat().st_size,
                "row_count": self.get_row_count(file_path),
                "schema": self.get_schema(file_path),
            }
        except Exception as exc:
            raise DataReaderError(f"Could not inspect {file_path.name}: {exc}") from exc

    @abstractmethod
    def load_sample(self, file_path: Path, limit: int = 100) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_schema(self, file_path: Path) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_row_count(self, file_path: Path) -> int | None:
        raise NotImplementedError

    def dataframe_schema(self, frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
        return {
            str(column): {
                "dtype": str(dtype),
                "nullable": bool(frame[column].isna().any()) if column in frame else None,
            }
            for column, dtype in frame.dtypes.items()
        }

    def dataframe_records(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        sanitized = frame.astype(object).where(pd.notna(frame), None)
        return [
            {str(key): self.to_json_safe(value) for key, value in row.items()}
            for row in sanitized.to_dict(orient="records")
        ]

    def to_json_safe(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if hasattr(value, "item"):
            try:
                return value.item()
            except ValueError:
                return value
        return value
