# Agent Workflows

The planned platform workflow follows a staged analytics and data operations path:

```text
Raw data asset
  -> Data Intake Agent
  -> Profiling Agent
  -> Cleaning Agent
  -> Data Quality Agent
  -> Query Agent
  -> Transformation / Modeling Agent
  -> Migration Readiness Agent
  -> Reporting / Insight Agent
```

## 1. Raw Data Asset

Inputs may include CSV, TSV, Excel, JSON, JSONL / NDJSON, Parquet, and SQLite database files.

## 2. Data Intake Agent

The intake stage identifies file type, captures metadata, records source information, and prepares the asset for downstream profiling. The current implementation provides this as a deterministic service, not an agent.

## 3. Profiling Agent

The profiling stage inspects schema, data types, null rates, duplicate records, cardinality, summary statistics, and suspicious values. The current implementation provides this as a deterministic profiling service that saves JSON reports under `reports/profiles/`.

These profile reports will later provide evidence for:

- Cleaning recommendations
- Data quality rules
- Query planning and semantic hints
- Migration readiness checks
- Reporting and insight summaries

## 4. Cleaning Agent

The cleaning stage will recommend and eventually apply safe cleanup actions such as trimming text, standardizing capitalization, parsing dates, handling invalid values, and deduplicating rows.

## 5. Data Quality Agent

The quality stage will validate datasets against technical checks and business rules, then produce pass/fail results and issue summaries.

## 6. Query Agent

The query stage will use DuckDB for local analytical querying. A later natural language interface can translate business questions into auditable SQL.

## 7. Transformation / Modeling Agent

The modeling stage will prepare reusable datasets, joins, metrics, and business-friendly views.

## 8. Migration Readiness Agent

The migration stage will assess whether datasets are ready for relational databases or warehouses by checking schema consistency, key quality, type compatibility, and load risks.

## 9. Reporting / Insight Agent

The reporting stage will create stakeholder-friendly summaries, data quality reports, migration notes, and business insights.

The current implementation covers the scaffold, sample data generation, multi-format intake foundation, and deterministic profiling foundation. Agent orchestration and LLM behavior are intentionally deferred.
