# Roadmap

## Milestone 1: Scaffold and Sample Data

Create project structure, documentation, configuration, basic FastAPI and Streamlit entry points, deterministic sample data generation, and initial tests.

## Milestone 2: Multi-Format Ingestion

Implemented the foundation: file readers for CSV, TSV, Excel, JSON, JSONL / NDJSON, Parquet, and SQLite files, plus FastAPI intake endpoints and simple metadata persistence.

## Milestone 3: Profiling Engine

Implemented the deterministic profiling foundation: dataset statistics, column statistics, quality summaries, warnings, SQLite table profiling, JSON report persistence, and FastAPI profiling endpoints.

## Milestone 4: Streamlit Upload UI

Create local upload and dataset browsing workflows in Streamlit.

## Milestone 5: Cleaning Agent

Add cleaning recommendations and safe transformations for common messy-data issues.

## Milestone 6: DuckDB Query Agent

Register ingested assets with DuckDB and support local analytical querying.

## Milestone 7: Data Quality Agent

Add validation rules, quality scoring, and quality reports.

## Milestone 8: Migration Readiness Agent

Assess datasets for warehouse or database migration readiness.

## Milestone 9: LangGraph Orchestration

Use LangGraph to coordinate agent workflows once individual stages are functional.

## Milestone 10: Portfolio Polish and Deployment

Improve UX, documentation, demo scenarios, screenshots, packaging, and deployment options.
