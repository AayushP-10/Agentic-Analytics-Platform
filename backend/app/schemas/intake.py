from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ColumnSchema(BaseModel):
    name: str
    dtype: str
    nullable: bool | None = None


class DataAssetMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    asset_id: str
    file_name: str
    file_path: str
    file_extension: str
    file_size_bytes: int
    format: str
    row_count: int | None = None
    column_count: int | None = None
    columns: list[str] = Field(default_factory=list)
    data_schema: dict[str, Any] = Field(default_factory=dict, alias="schema")
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
