from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api import types as pd_types

from backend.app.core.settings import DEFAULT_PROFILING_ROW_LIMIT, PROFILE_REPORTS_DIR
from backend.app.schemas.intake import DataAssetMetadata
from backend.app.schemas.profiling import (
    BooleanColumnProfile,
    CategoricalColumnProfile,
    ColumnProfile,
    DataQualitySummary,
    DatasetProfile,
    DatetimeColumnProfile,
    NumericColumnProfile,
    ProfilingWarning,
)
from backend.app.services.data_intake_service import DataIntakeService, IntakeFileError


class ProfilingError(ValueError):
    pass


class ProfilingService:
    def __init__(
        self,
        intake_service: DataIntakeService | None = None,
        reports_dir: Path = PROFILE_REPORTS_DIR,
        row_limit: int = DEFAULT_PROFILING_ROW_LIMIT,
    ) -> None:
        self.intake_service = intake_service or DataIntakeService()
        self.reports_dir = reports_dir
        self.row_limit = row_limit

    def profile_asset(self, asset_id: str, table_name: str | None = None) -> DatasetProfile:
        try:
            metadata = self.intake_service.get_asset(asset_id)
        except IntakeFileError as exc:
            raise ProfilingError(str(exc)) from exc
        return self.profile_file(Path(metadata.file_path), metadata=metadata, table_name=table_name)

    def profile_file(
        self,
        file_path: Path,
        metadata: DataAssetMetadata | None = None,
        table_name: str | None = None,
    ) -> DatasetProfile:
        if metadata is None:
            metadata = self.intake_service.inspect_file(file_path)

        frame, source_row_count, selected_table = self._load_frame(
            Path(metadata.file_path),
            metadata.format,
            table_name=table_name,
        )
        warnings: list[ProfilingWarning] = []
        if source_row_count > len(frame):
            warnings.append(
                ProfilingWarning(
                    warning_type="sample_based_profile",
                    message=(
                        f"Profile is based on the first {len(frame)} rows out of "
                        f"{source_row_count} available rows."
                    ),
                    severity="info",
                )
            )

        row_count = len(frame)
        column_count = len(frame.columns)
        duplicate_row_count = (
            int(self._hashable_frame(frame).duplicated().sum()) if row_count else 0
        )
        duplicate_row_percentage = self._percentage(duplicate_row_count, row_count)
        missing_cell_count = int(frame.isna().sum().sum()) if column_count else 0
        total_cells = row_count * column_count
        missing_cell_percentage = self._percentage(missing_cell_count, total_cells)

        if duplicate_row_count:
            warnings.append(
                ProfilingWarning(
                    warning_type="duplicate_rows",
                    message="Dataset contains duplicate rows.",
                    severity="warning",
                )
            )

        column_profiles = [
            self._profile_column(frame[column], row_count) for column in frame.columns
        ]
        quality_summary = self._quality_summary(
            column_profiles,
            duplicate_row_count=duplicate_row_count,
            duplicate_row_percentage=duplicate_row_percentage,
            missing_cell_percentage=missing_cell_percentage,
        )
        warnings.extend(self._flatten_column_warnings(column_profiles))

        profile_id = self._profile_id(metadata.asset_id, selected_table)
        report_path = self.reports_dir / f"{profile_id}.json"
        profile = DatasetProfile(
            profile_id=profile_id,
            asset_id=metadata.asset_id,
            file_name=metadata.file_name,
            format=metadata.format,
            generated_at=datetime.now(UTC),
            row_count=row_count,
            column_count=column_count,
            memory_usage_estimate_bytes=int(frame.memory_usage(deep=True).sum()),
            duplicate_row_count=duplicate_row_count,
            duplicate_row_percentage=duplicate_row_percentage,
            missing_cell_count=missing_cell_count,
            missing_cell_percentage=missing_cell_percentage,
            columns=column_profiles,
            quality_summary=quality_summary,
            warnings=warnings,
            sample_rows=self._sample_rows(frame),
            report_path=str(report_path),
            table_name=selected_table,
        )
        self.save_profile(profile)
        return profile

    def list_reports(self) -> list[dict[str, Any]]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        reports = []
        for path in sorted(self.reports_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            reports.append(
                {
                    "profile_id": payload.get("profile_id", path.stem),
                    "asset_id": payload.get("asset_id"),
                    "file_name": payload.get("file_name"),
                    "format": payload.get("format"),
                    "generated_at": payload.get("generated_at"),
                    "report_path": str(path),
                    "table_name": payload.get("table_name"),
                }
            )
        return reports

    def get_report(self, profile_id: str) -> DatasetProfile:
        path = self.reports_dir / f"{profile_id}.json"
        if not path.exists():
            raise ProfilingError(f"Profile report not found: {profile_id}")
        with path.open("r", encoding="utf-8") as file:
            return DatasetProfile.model_validate(json.load(file))

    def save_profile(self, profile: DatasetProfile) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        with Path(profile.report_path).open("w", encoding="utf-8") as file:
            json.dump(profile.model_dump(mode="json"), file, indent=2)

    def _load_frame(
        self,
        file_path: Path,
        file_format: str,
        table_name: str | None = None,
    ) -> tuple[pd.DataFrame, int, str | None]:
        if file_format == "csv":
            return self._read_csv(file_path, ","), self._count_csv_rows(file_path, ","), None
        if file_format == "tsv":
            return self._read_csv(file_path, "\t"), self._count_csv_rows(file_path, "\t"), None
        if file_format == "excel":
            frame = pd.read_excel(file_path, nrows=self.row_limit)
            return frame, len(pd.read_excel(file_path, usecols=[0])), None
        if file_format == "json":
            frame = pd.read_json(file_path).head(self.row_limit)
            return frame, len(pd.read_json(file_path)), None
        if file_format == "jsonl":
            frame = pd.read_json(file_path, lines=True, nrows=self.row_limit)
            return frame, self._count_jsonl_rows(file_path), None
        if file_format == "parquet":
            source_rows = pd.read_parquet(file_path, columns=[]).shape[0]
            return pd.read_parquet(file_path).head(self.row_limit), source_rows, None
        if file_format == "sqlite":
            return self._read_sqlite(file_path, table_name)
        raise ProfilingError(f"Unsupported format for profiling: {file_format}")

    def _read_csv(self, file_path: Path, sep: str) -> pd.DataFrame:
        return pd.read_csv(file_path, sep=sep, nrows=self.row_limit)

    def _count_csv_rows(self, file_path: Path, sep: str) -> int:
        chunks = pd.read_csv(file_path, sep=sep, chunksize=100_000, usecols=[0])
        return sum(len(chunk) for chunk in chunks)

    def _count_jsonl_rows(self, file_path: Path) -> int:
        with file_path.open("r", encoding="utf-8") as file:
            return sum(1 for line in file if line.strip())

    def _read_sqlite(
        self,
        file_path: Path,
        table_name: str | None,
    ) -> tuple[pd.DataFrame, int, str]:
        with sqlite3.connect(file_path) as connection:
            tables = [
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
                ).fetchall()
            ]
            if not tables:
                raise ProfilingError("SQLite database has no user tables to profile.")
            selected_table = table_name or tables[0]
            if selected_table not in tables:
                raise ProfilingError(
                    f"SQLite table '{selected_table}' was not found. Available tables: {tables}"
                )
            frame = pd.read_sql_query(
                f'SELECT * FROM "{selected_table}" LIMIT ?',
                connection,
                params=(self.row_limit,),
            )
            source_rows = int(
                connection.execute(f'SELECT COUNT(*) FROM "{selected_table}"').fetchone()[0]
            )
        return frame, source_rows, selected_table

    def _profile_column(self, series: pd.Series, row_count: int) -> ColumnProfile:
        non_null = series.dropna()
        null_count = int(series.isna().sum())
        hashable_non_null = self._hashable_series(non_null)
        unique_count = int(hashable_non_null.nunique(dropna=True))
        duplicate_value_count = int(max(len(non_null) - unique_count, 0))
        inferred_type = self._infer_type(series)
        warnings = self._base_column_warnings(series, inferred_type, row_count, unique_count)

        profile = ColumnProfile(
            column_name=str(series.name),
            inferred_type=inferred_type,
            source_dtype=str(series.dtype),
            non_null_count=int(non_null.count()),
            null_count=null_count,
            null_percentage=self._percentage(null_count, row_count),
            unique_count=unique_count,
            unique_percentage=self._percentage(unique_count, row_count),
            duplicate_value_count=duplicate_value_count,
            sample_values=self._sample_values(non_null),
            warnings=warnings,
        )
        if inferred_type == "numeric":
            profile.numeric_profile = self._numeric_profile(series, warnings)
        elif inferred_type == "datetime":
            profile.datetime_profile = self._datetime_profile(series, warnings)
        elif inferred_type == "boolean":
            profile.boolean_profile = self._boolean_profile(series)
        else:
            profile.categorical_profile = self._categorical_profile(series, row_count, warnings)
        profile.warnings = warnings
        return profile

    def _infer_type(self, series: pd.Series) -> str:
        if pd_types.is_bool_dtype(series):
            return "boolean"
        if pd_types.is_numeric_dtype(series):
            return "numeric"
        if pd_types.is_datetime64_any_dtype(series):
            return "datetime"

        non_null = series.dropna()
        if non_null.empty:
            return "categorical"
        lowered = non_null.astype(str).str.strip().str.lower()
        if set(lowered.unique()).issubset({"true", "false", "0", "1", "yes", "no"}):
            return "boolean"

        name = str(series.name).lower()
        if "date" not in name and "time" not in name:
            return "categorical"

        parsed = pd.to_datetime(non_null, errors="coerce")
        parse_rate = float(parsed.notna().mean())
        if parse_rate >= 0.8:
            return "datetime"
        return "categorical"

    def _base_column_warnings(
        self,
        series: pd.Series,
        inferred_type: str,
        row_count: int,
        unique_count: int,
    ) -> list[ProfilingWarning]:
        warnings: list[ProfilingWarning] = []
        column_name = str(series.name)
        null_percentage = self._percentage(int(series.isna().sum()), row_count)
        unique_percentage = self._percentage(unique_count, row_count)
        lowered_name = column_name.lower()

        if null_percentage > 30:
            warnings.append(
                ProfilingWarning(
                    column_name=column_name,
                    warning_type="high_missing_values",
                    message="Column has more than 30% missing values.",
                    severity="warning",
                )
            )
        if unique_percentage >= 90 or lowered_name.endswith("_id") or lowered_name == "id":
            warnings.append(
                ProfilingWarning(
                    column_name=column_name,
                    warning_type="possible_identifier",
                    message="Column appears to be an identifier.",
                    severity="info",
                )
            )
        if inferred_type == "datetime":
            parsed = pd.to_datetime(series.dropna(), errors="coerce")
            if int(parsed.isna().sum()):
                warnings.append(
                    ProfilingWarning(
                        column_name=column_name,
                        warning_type="invalid_dates",
                        message="Column may contain invalid dates.",
                        severity="warning",
                    )
                )
        if "email" in lowered_name:
            valid = series.dropna().astype(str).str.contains(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
            if int((~valid).sum()):
                warnings.append(
                    ProfilingWarning(
                        column_name=column_name,
                        warning_type="invalid_email_values",
                        message="Column may contain invalid email values.",
                        severity="warning",
                    )
                )
        return warnings

    def _numeric_profile(
        self,
        series: pd.Series,
        warnings: list[ProfilingWarning],
    ) -> NumericColumnProfile:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return NumericColumnProfile()
        q1 = numeric.quantile(0.25)
        q3 = numeric.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        outlier_count = int(((numeric < lower_bound) | (numeric > upper_bound)).sum()) if iqr else 0
        negative_count = int((numeric < 0).sum())
        column_name = str(series.name)
        if negative_count:
            warnings.append(
                ProfilingWarning(
                    column_name=column_name,
                    warning_type="negative_values",
                    message="Column contains negative values.",
                    severity="warning",
                )
            )
        if outlier_count:
            warnings.append(
                ProfilingWarning(
                    column_name=column_name,
                    warning_type="possible_outliers",
                    message="Numeric column has possible outliers.",
                    severity="info",
                )
            )
        return NumericColumnProfile(
            min=float(numeric.min()),
            max=float(numeric.max()),
            mean=float(numeric.mean()),
            median=float(numeric.median()),
            standard_deviation=float(numeric.std()) if len(numeric) > 1 else 0.0,
            zero_count=int((numeric == 0).sum()),
            negative_count=negative_count,
            outlier_count=outlier_count,
            outlier_percentage=self._percentage(outlier_count, len(numeric)),
        )

    def _categorical_profile(
        self,
        series: pd.Series,
        row_count: int,
        warnings: list[ProfilingWarning],
    ) -> CategoricalColumnProfile:
        text = series.dropna().astype(str)
        stripped = text.str.strip()
        blank_count = int((stripped == "").sum())
        possible_high_cardinality = self._percentage(stripped.nunique(), row_count) >= 80
        column_name = str(series.name)
        if possible_high_cardinality:
            warnings.append(
                ProfilingWarning(
                    column_name=column_name,
                    warning_type="high_cardinality",
                    message="Column has high cardinality.",
                    severity="info",
                )
            )
        if blank_count:
            warnings.append(
                ProfilingWarning(
                    column_name=column_name,
                    warning_type="blank_strings",
                    message="Text column has blank strings.",
                    severity="warning",
                )
            )
        lengths = stripped.map(len)
        return CategoricalColumnProfile(
            top_values={str(k): int(v) for k, v in stripped.value_counts().head(10).items()},
            average_length=float(lengths.mean()) if not lengths.empty else None,
            min_length=int(lengths.min()) if not lengths.empty else None,
            max_length=int(lengths.max()) if not lengths.empty else None,
            blank_string_count=blank_count,
            possible_high_cardinality=possible_high_cardinality,
        )

    def _datetime_profile(
        self,
        series: pd.Series,
        warnings: list[ProfilingWarning],
    ) -> DatetimeColumnProfile:
        parsed = pd.to_datetime(series.dropna(), errors="coerce")
        valid = parsed.dropna()
        invalid_count = int(parsed.isna().sum())
        if invalid_count:
            warnings.append(
                ProfilingWarning(
                    column_name=str(series.name),
                    warning_type="invalid_dates",
                    message="Column may contain invalid dates.",
                    severity="warning",
                )
            )
        if valid.empty:
            return DatetimeColumnProfile(invalid_date_count=invalid_count)
        min_date = valid.min().to_pydatetime()
        max_date = valid.max().to_pydatetime()
        return DatetimeColumnProfile(
            min_date=min_date,
            max_date=max_date,
            invalid_date_count=invalid_count,
            date_range_days=(max_date - min_date).days,
        )

    def _boolean_profile(self, series: pd.Series) -> BooleanColumnProfile:
        values = series.dropna().astype(str).str.strip().str.lower()
        true_count = int(values.isin({"true", "1", "yes"}).sum())
        false_count = int(values.isin({"false", "0", "no"}).sum())
        total = true_count + false_count
        return BooleanColumnProfile(
            true_count=true_count,
            false_count=false_count,
            true_percentage=self._percentage(true_count, total),
            false_percentage=self._percentage(false_count, total),
        )

    def _quality_summary(
        self,
        columns: list[ColumnProfile],
        duplicate_row_count: int,
        duplicate_row_percentage: float,
        missing_cell_percentage: float,
    ) -> DataQualitySummary:
        columns_with_missing = [c.column_name for c in columns if c.null_count > 0]
        high_missing = [c.column_name for c in columns if c.null_percentage > 30]
        high_cardinality = [
            c.column_name
            for c in columns
            if c.categorical_profile and c.categorical_profile.possible_high_cardinality
        ]
        outlier_columns = [
            c.column_name
            for c in columns
            if c.numeric_profile and c.numeric_profile.outlier_count > 0
        ]
        identifiers = [
            c.column_name
            for c in columns
            if any(w.warning_type == "possible_identifier" for w in c.warnings)
        ]
        datetime_columns = [c.column_name for c in columns if c.inferred_type == "datetime"]
        amount_columns = [
            c.column_name
            for c in columns
            if c.inferred_type == "numeric"
            and any(
                token in c.column_name.lower()
                for token in ["amount", "price", "cost", "value"]
            )
        ]
        categorical_columns = [c.column_name for c in columns if c.inferred_type == "categorical"]
        invalid_warning_count = sum(
            1
            for c in columns
            for w in c.warnings
            if w.warning_type in {"invalid_dates", "invalid_email_values", "negative_values"}
        )

        completeness = max(0.0, 100.0 - missing_cell_percentage)
        uniqueness = max(0.0, 100.0 - duplicate_row_percentage)
        consistency = max(0.0, 100.0 - (len(high_cardinality) * 5) - (len(high_missing) * 10))
        validity = max(0.0, 100.0 - (invalid_warning_count * 10))
        overall = round((completeness + uniqueness + consistency + validity) / 4, 2)

        next_steps = []
        if columns_with_missing:
            next_steps.append("Review missing values and decide fill, drop, or exception rules.")
        if duplicate_row_count:
            next_steps.append("Review duplicate rows before downstream modeling or migration.")
        if outlier_columns:
            next_steps.append(
                "Investigate numeric outliers for data entry errors or real extremes."
            )
        if identifiers:
            next_steps.append("Confirm identifier columns and uniqueness expectations.")
        if not next_steps:
            next_steps.append("Proceed to profiling review and define data quality rules.")

        return DataQualitySummary(
            overall_quality_score=overall,
            completeness_score=round(completeness, 2),
            uniqueness_score=round(uniqueness, 2),
            consistency_score=round(consistency, 2),
            validity_score=round(validity, 2),
            columns_with_missing_values=columns_with_missing,
            columns_with_high_missing_percentage=high_missing,
            columns_with_high_cardinality=high_cardinality,
            numeric_columns_with_outliers=outlier_columns,
            suspected_identifier_columns=identifiers,
            suspected_datetime_columns=datetime_columns,
            suspected_currency_or_amount_columns=amount_columns,
            suspected_categorical_columns=categorical_columns,
            duplicate_rows_detected=duplicate_row_count > 0,
            recommended_next_steps=next_steps,
        )

    def _flatten_column_warnings(self, columns: list[ColumnProfile]) -> list[ProfilingWarning]:
        return [warning for column in columns for warning in column.warnings]

    def _sample_values(self, series: pd.Series) -> list[Any]:
        values = series.head(5).astype(object).where(pd.notna(series.head(5)), None)
        return [self._json_safe(value) for value in values.tolist()]

    def _sample_rows(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        sample = frame.head(10).astype(object).where(pd.notna(frame.head(10)), None)
        return [
            {str(key): self._json_safe(value) for key, value in row.items()}
            for row in sample.to_dict(orient="records")
        ]

    def _hashable_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        return frame.map(
            lambda value: json.dumps(value, sort_keys=True)
            if isinstance(value, dict | list)
            else value
        )

    def _hashable_series(self, series: pd.Series) -> pd.Series:
        return series.map(
            lambda value: json.dumps(value, sort_keys=True)
            if isinstance(value, dict | list)
            else value
        )

    def _json_safe(self, value: Any) -> Any:
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

    def _profile_id(self, asset_id: str, table_name: str | None) -> str:
        generated_at = datetime.now(UTC).isoformat()
        raw = f"{asset_id}|{table_name or ''}|{generated_at}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _percentage(self, numerator: int | float, denominator: int | float) -> float:
        if not denominator:
            return 0.0
        return round((float(numerator) / float(denominator)) * 100, 2)
