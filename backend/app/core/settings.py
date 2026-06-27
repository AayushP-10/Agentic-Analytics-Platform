from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"
PROFILE_REPORTS_DIR = REPORTS_DIR / "profiles"
INTAKE_METADATA_PATH = RAW_DATA_DIR / ".metadata.json"
MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024
DEFAULT_PROFILING_ROW_LIMIT = 50_000

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".tsv",
    ".xlsx",
    ".json",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".db",
    ".sqlite",
    ".sqlite3",
}
