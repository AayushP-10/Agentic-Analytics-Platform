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
Services, schemas, utilities, and future agents
       |
       v
Local data assets, DuckDB, SQLite metadata, generated reports
```

The backend will expose application APIs and coordinate services. The frontend will provide analyst-facing workflows such as upload, profiling review, cleaning review, query, quality reporting, and migration readiness review.

## Frontend and Backend Separation

The `frontend/` directory contains the Streamlit application. It is intended for fast local demos, analyst workflows, and portfolio presentation.

The `backend/` directory contains the FastAPI application. It will eventually own API routes, schemas, agent coordination, service logic, metadata persistence, and background workflow execution.

Keeping these layers separate makes it easier to evolve from a local demo into a service-oriented application without rewriting the main workflow concepts.

## Data Folder Structure

- `data/raw/`: raw user-provided files before processing.
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

- Data Intake Agent accepts files and records metadata.
- Profiling Agent summarizes schema, distributions, nulls, duplicates, and anomalies.
- Cleaning Agent proposes and applies cleanup actions.
- Data Quality Agent validates business and technical rules.
- Query Agent translates natural language questions into local analytical queries.
- Transformation / Modeling Agent prepares reusable modeled datasets.
- Migration Readiness Agent assesses database or warehouse readiness.
- Reporting / Insight Agent produces stakeholder-facing summaries.

LangGraph is planned as the orchestration layer once individual capabilities exist. The project does not implement agent orchestration in the first milestone.

## Local-First and Free-Tier Friendly

The project is designed to run locally with open-source tools. DuckDB, SQLite, Pandas, Polars, and PyArrow provide a practical analytics stack without paid infrastructure. LLM integration is optional and disabled by default through `LLM_PROVIDER=none`, allowing the core workflows to remain usable without API keys.
