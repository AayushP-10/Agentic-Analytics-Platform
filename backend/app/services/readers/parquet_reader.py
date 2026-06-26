from __future__ import annotations

from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from backend.app.services.readers.base import DataReader, DataReaderError


class ParquetReader(DataReader):
    supported_extensions = {".parquet"}
    format_name = "parquet"

    def load_sample(self, file_path: Path, limit: int = 100) -> list[dict[str, Any]]:
        try:
            parquet_file = pq.ParquetFile(file_path)
            batch = next(parquet_file.iter_batches(batch_size=limit), None)
            if batch is None:
                return []
            return self.dataframe_records(batch.to_pandas())
        except Exception as exc:
            raise DataReaderError(f"Could not load sample from {file_path.name}: {exc}") from exc

    def get_schema(self, file_path: Path) -> dict[str, Any]:
        try:
            parquet_file = pq.ParquetFile(file_path)
            return {
                field.name: {
                    "dtype": str(field.type),
                    "nullable": field.nullable,
                }
                for field in parquet_file.schema_arrow
            }
        except Exception as exc:
            raise DataReaderError(f"Could not infer schema for {file_path.name}: {exc}") from exc

    def get_row_count(self, file_path: Path) -> int | None:
        try:
            return pq.ParquetFile(file_path).metadata.num_rows
        except Exception as exc:
            raise DataReaderError(f"Could not count rows for {file_path.name}: {exc}") from exc
