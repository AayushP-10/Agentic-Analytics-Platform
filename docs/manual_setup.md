# Manual Setup

Complete these steps before running the project locally.

## 1. Clone the Repository

```bash
git clone <repository-url>
cd agentic-analytics-platform
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```bash
python -m pip install --upgrade pip
make install
```

## 4. Create a Local Environment File

```bash
cp .env.example .env
```

Do not commit `.env` or any real secrets.

## 5. Generate Sample Data

```bash
make sample-data
```

This creates deterministic demo files under `data/sample/` and `data/sqlite/`.

## 6. Run Tests

```bash
make test
```

The tests generate temporary sample files and verify reader and profiling behavior for CSV, TSV, Excel, JSON, JSONL / NDJSON, Parquet, and SQLite.

## 7. Run Linting

```bash
make lint
```

## 8. Start the Backend

```bash
make backend
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

Upload a generated CSV sample:

```bash
curl -X POST "http://127.0.0.1:8000/api/intake/upload" \
  -F "file=@data/sample/customers.csv"
```

List ingested assets:

```bash
curl "http://127.0.0.1:8000/api/intake/assets"
```

Create a profile for an ingested asset:

```bash
curl -X POST "http://127.0.0.1:8000/api/profiling/assets/<asset_id>"
```

For SQLite, provide a table name when needed:

```bash
curl -X POST "http://127.0.0.1:8000/api/profiling/assets/<asset_id>?table_name=orders"
```

List saved profile reports:

```bash
curl "http://127.0.0.1:8000/api/profiling/reports"
```

Profile JSON reports are saved under `reports/profiles/`.

## 9. Start the Frontend

```bash
make frontend
```

Streamlit will print a local URL in the terminal.
