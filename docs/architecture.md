# Architecture

Agentic Analytics Platform is planned as a local-first analytics and data operations system. The first version separates the user interface, API layer, data processing services, and future agent orchestration boundaries while keeping the repository simple enough to run on a developer laptop.

## High-Level Architecture

```text
Streamlit frontend
       |
       v
FastAPI backend
       |
       v
Data intake service, profiling service, readers, schemas, utilities, and future agents
       |
       v
Local data assets, DuckDB, SQLite metadata, generated reports
```

The backend will expose application APIs and coordinate services. The frontend will provide analyst-facing workflows such as upload, profiling review, cleaning review, query, quality reporting, and migration readiness review.

The current backend includes a multi-format intake layer. API routes accept uploads, persist raw files under `data/raw/`, select a reader based on extension, inspect metadata, and store simple JSON metadata for later lookup.

The backend also includes a deterministic profiling layer. It uses the existing intake metadata when available, loads a bounded number of rows, computes dataset and column statistics, and saves profile reports under `reports/profiles/`.

## Frontend and Backend Separation

The `frontend/` directory contains the Streamlit application. It is intended for fast local demos, analyst workflows, and portfolio presentation.

The `backend/` directory contains the FastAPI application. It will eventually own API routes, schemas, agent coordination, service logic, metadata persistence, and background workflow execution.

Keeping these layers separate makes it easier to evolve from a local demo into a service-oriented application without rewriting the main workflow concepts.

## Data Folder Structure

- `data/raw/`: raw user-provided files before processing, plus simple `.metadata.json` intake records.
- `data/processed/`: cleaned, normalized, or transformed outputs.
- `data/sample/`: deterministic synthetic datasets for testing and demos.
- `data/sqlite/`: local SQLite databases for metadata and database-ingestion examples.

Generated data files are intentionally ignored by git, while `.gitkeep` files preserve the directory structure.

## Reports Folder Structure

- `reports/profiles/`: profiling outputs.
- `reports/cleaning/`: cleaning recommendations and change summaries.
- `reports/quality/`: data quality results.
- `reports/migration/`: migration readiness reports.
- `reports/insights/`: business insight outputs.

## Agent-Based Design

The planned agents represent specialized stages of an analytics workflow:

- Data Intake Agent accepts files and records metadata. The current intake service is the non-agent foundation for this capability.
- Profiling Agent summarizes schema, distributions, nulls, duplicates, and anomalies. The current profiling service is the deterministic non-agent foundation for this capability.
- Cleaning Agent proposes and applies cleanup actions.
- Data Quality Agent validates business and technical rules.
- Query Agent translates natural language questions into local analytical queries.
- Transformation / Modeling Agent prepares reusable modeled datasets.
- Migration Readiness Agent assesses database or warehouse readiness.
- Reporting / Insight Agent produces stakeholder-facing summaries.

LangGraph is planned as the orchestration layer once individual capabilities exist. The project does not implement agent orchestration in the first milestone.

## Reader-Based Intake Design

The intake engine uses a small reader interface under `backend/app/services/readers/`. Each reader is responsible for extension detection, schema inference, sample loading, row counting, and basic metadata extraction for one format family.

Supported readers:

- `CSVReader`
- `TSVReader`
- `ExcelReader`
- `JSONReader`
- `JSONLReader`
- `ParquetReader`
- `SQLiteReader`

The service layer standardizes reader output into one metadata response shape. Upload handling includes filename sanitization, supported-extension checks, path traversal prevention through safe destination construction, and a 100 MB upload limit.

## Profiling Design

The profiling service lives under `backend/app/services/profiling_service.py`. It accepts an `asset_id` or file path, reuses intake metadata when available, and supports the same MVP formats as intake.

Profiling differs from intake:

- Intake registers an asset and extracts lightweight metadata.
- Profiling analyzes the data values and produces detailed statistics, warnings, and quality summaries.

The profiler computes:

- Dataset row and column counts
- Missing cell counts and percentages
- Duplicate row counts and percentages
- Memory usage estimate
- Column-level nulls, uniqueness, duplicate values, and sample values
- Numeric min, max, mean, median, standard deviation, negative values, zeroes, and IQR outliers
- Categorical top values, text lengths, blanks, and high-cardinality hints
- Datetime ranges and invalid date counts where detectable
- Boolean true/false distribution
- Deterministic quality scores and recommended next steps

Reports are saved as JSON files in `reports/profiles/`. These reports are intended to feed future cleaning, data quality, query, migration readiness, and reporting agents.

## Local-First and Free-Tier Friendly

The project is designed to run locally with open-source tools. DuckDB, SQLite, Pandas, Polars, and PyArrow provide a practical analytics stack without paid infrastructure. LLM integration is optional and disabled by default through `LLM_PROVIDER=none`, allowing the core workflows to remain usable without API keys.
