from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from backend.app.services.readers.base import DataReader, DataReaderError


class SQLiteReader(DataReader):
    supported_extensions = {".db", ".sqlite", ".sqlite3"}
    format_name = "sqlite"

    def load_sample(self, file_path: Path, limit: int = 100) -> list[dict[str, Any]]:
        try:
            with sqlite3.connect(file_path) as connection:
                connection.row_factory = sqlite3.Row
                table = self._default_table(connection)
                if table is None:
                    return []
                rows = connection.execute(
                    f'SELECT * FROM "{table}" LIMIT ?',
                    (limit,),
                ).fetchall()
                return [dict(row) for row in rows]
        except Exception as exc:
            raise DataReaderError(f"Could not load sample from {file_path.name}: {exc}") from exc

    def get_schema(self, file_path: Path) -> dict[str, Any]:
        try:
            with sqlite3.connect(file_path) as connection:
                tables = self._list_tables(connection)
                table_schemas = {}
                for table in tables:
                    columns = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
                    table_schemas[table] = {
                        column[1]: {
                            "dtype": column[2],
                            "nullable": not bool(column[3]),
                            "primary_key": bool(column[5]),
                        }
                        for column in columns
                    }
                return {
                    "default_table": tables[0] if tables else None,
                    "tables": table_schemas,
                }
        except Exception as exc:
            raise DataReaderError(f"Could not infer schema for {file_path.name}: {exc}") from exc

    def get_row_count(self, file_path: Path) -> int | None:
        try:
            with sqlite3.connect(file_path) as connection:
                table = self._default_table(connection)
                if table is None:
                    return None
                return int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
        except Exception as exc:
            raise DataReaderError(f"Could not count rows for {file_path.name}: {exc}") from exc

    def list_tables(self, file_path: Path) -> list[str]:
        try:
            with sqlite3.connect(file_path) as connection:
                return self._list_tables(connection)
        except Exception as exc:
            raise DataReaderError(f"Could not list tables for {file_path.name}: {exc}") from exc

    def _list_tables(self, connection: sqlite3.Connection) -> list[str]:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
        return [str(row[0]) for row in rows]

    def _default_table(self, connection: sqlite3.Connection) -> str | None:
        tables = self._list_tables(connection)
        return tables[0] if tables else None
