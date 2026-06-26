# Agentic Analytics Platform

Agentic Analytics Platform is a local-first, free/open-source analytics and data operations project. It is designed to help teams ingest raw datasets, profile them, clean messy records, validate quality, query data in natural language, generate business insights, and prepare assets for migration to databases or warehouses.

The current implementation includes the initial scaffold, deterministic sample data generation, and a multi-format data intake engine for registering and inspecting raw assets.

## Why This Exists

Modern data work often spans analysts, analytics engineers, platform teams, and business stakeholders. This project simulates that enterprise workflow in a portfolio-friendly local environment without requiring paid cloud services or proprietary data.

The long-term goal is to demonstrate how agentic workflows can coordinate practical data operations while remaining auditable, reproducible, and useful for real analytics tasks.

## Enterprise Workflow Simulated

The platform will eventually model a full data operations path:

1. Accept raw business data assets.
2. Profile files and databases for structure, types, nulls, and anomalies.
3. Recommend and apply cleaning steps.
4. Validate quality rules and business constraints.
5. Query data through DuckDB and natural language interfaces.
6. Prepare transformations and analytics models.
7. Assess migration readiness for databases or warehouses.
8. Produce reports and business insights.

## Planned Agents

- Data Intake Agent
- Profiling Agent
- Cleaning Agent
- Data Quality Agent
- Query Agent
- Transformation / Modeling Agent
- Migration Readiness Agent
- Reporting / Insight Agent

## Planned Architecture

- FastAPI backend for application APIs and orchestration boundaries.
- Streamlit frontend for local analyst workflows and demos.
- Multi-format data intake service for raw asset registration and metadata extraction.
- DuckDB for local analytical querying.
- Pandas, Polars, and PyArrow for data processing.
- SQLite for app metadata and database-ingestion demos.
- LangGraph for future multi-agent orchestration.
- LangChain where it adds useful integration value.
- Local folders for raw data, processed data, generated reports, and sample assets.

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangGraph, planned for future orchestration
- LangChain, planned where useful
- DuckDB
- Pandas / Polars
- PyArrow
- Pydantic
- SQLite
- Pytest
- Ruff

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
make install
cp .env.example .env
make sample-data
make test
make lint
```

Start the backend:

```bash
make backend
```

Start the frontend:

```bash
make frontend
```

## Data Intake Engine

The backend can inspect and register these MVP formats:

- CSV
- TSV
- Excel `.xlsx`
- JSON
- JSONL / NDJSON
- Parquet
- SQLite database files: `.db`, `.sqlite`, `.sqlite3`

The intake API extracts standardized metadata including asset ID, file name, extension, size, format, row count, column count, columns, schema, sample rows, warnings, and creation timestamp.

Upload a file while the backend is running:

```bash
curl -X POST "http://127.0.0.1:8000/api/intake/upload" \
  -F "file=@data/sample/customers.csv"
```

List known raw assets:

```bash
curl "http://127.0.0.1:8000/api/intake/assets"
```

## Current Status

Milestones 1 and 2 foundations are implemented:

- Project structure
- FastAPI health endpoint
- Minimal Streamlit placeholder
- Documentation
- Python packaging and tooling configuration
- Deterministic synthetic sample data generator
- Initial tests for health checks and generated data files
- Reader classes for CSV, TSV, Excel, JSON, JSONL / NDJSON, Parquet, and SQLite
- Data intake service with file safety checks and JSON metadata persistence
- FastAPI intake upload and asset listing endpoints

No Cleaning Agent, Query Agent, Data Quality Agent, Migration Readiness Agent, LangGraph workflow, LLM calls, or Streamlit upload UI has been implemented yet.

## MVP Roadmap

1. Scaffold and sample data
2. Multi-format ingestion
3. Profiling engine
4. Streamlit upload UI
5. Cleaning agent
6. DuckDB query agent
7. Data quality agent
8. Migration readiness agent
9. LangGraph orchestration
10. Portfolio polish and deployment

## Manual Steps

- Clone the repository.
- Create and activate a Python virtual environment.
- Install dependencies with `make install`.
- Copy `.env.example` to `.env`.
- Generate sample data with `make sample-data`.
- Run tests with `make test`.
- Run linting with `make lint`.
- Start the backend with `make backend`.
- Start the frontend with `make frontend`.
