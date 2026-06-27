from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ProfilingWarning(BaseModel):
    column_name: str | None = None
    warning_type: str
    message: str
    severity: str = "info"


class NumericColumnProfile(BaseModel):
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    standard_deviation: float | None = None
    zero_count: int = 0
    negative_count: int = 0
    outlier_count: int = 0
    outlier_percentage: float = 0.0


class CategoricalColumnProfile(BaseModel):
    top_values: dict[str, int] = Field(default_factory=dict)
    average_length: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    blank_string_count: int = 0
    possible_high_cardinality: bool = False


class DatetimeColumnProfile(BaseModel):
    min_date: datetime | None = None
    max_date: datetime | None = None
    invalid_date_count: int = 0
    date_range_days: int | None = None


class BooleanColumnProfile(BaseModel):
    true_count: int = 0
    false_count: int = 0
    true_percentage: float = 0.0
    false_percentage: float = 0.0


class ColumnProfile(BaseModel):
    column_name: str
    inferred_type: str
    source_dtype: str
    non_null_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    duplicate_value_count: int
    sample_values: list[Any] = Field(default_factory=list)
    warnings: list[ProfilingWarning] = Field(default_factory=list)
    numeric_profile: NumericColumnProfile | None = None
    categorical_profile: CategoricalColumnProfile | None = None
    datetime_profile: DatetimeColumnProfile | None = None
    boolean_profile: BooleanColumnProfile | None = None


class DataQualitySummary(BaseModel):
    overall_quality_score: float
    completeness_score: float
    uniqueness_score: float
    consistency_score: float
    validity_score: float
    columns_with_missing_values: list[str] = Field(default_factory=list)
    columns_with_high_missing_percentage: list[str] = Field(default_factory=list)
    columns_with_high_cardinality: list[str] = Field(default_factory=list)
    numeric_columns_with_outliers: list[str] = Field(default_factory=list)
    suspected_identifier_columns: list[str] = Field(default_factory=list)
    suspected_datetime_columns: list[str] = Field(default_factory=list)
    suspected_currency_or_amount_columns: list[str] = Field(default_factory=list)
    suspected_categorical_columns: list[str] = Field(default_factory=list)
    duplicate_rows_detected: bool = False
    recommended_next_steps: list[str] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    profile_id: str
    asset_id: str
    file_name: str
    format: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    row_count: int
    column_count: int
    memory_usage_estimate_bytes: int | None = None
    duplicate_row_count: int
    duplicate_row_percentage: float
    missing_cell_count: int
    missing_cell_percentage: float
    columns: list[ColumnProfile]
    quality_summary: DataQualitySummary
    warnings: list[ProfilingWarning] = Field(default_factory=list)
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)
    report_path: str
    table_name: str | None = None
