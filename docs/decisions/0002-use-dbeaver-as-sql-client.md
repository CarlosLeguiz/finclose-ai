# ADR 0002 — Use DBeaver as SQL client for DuckDB exploration

**Status:** Accepted
**Date:** 2026-06-02
**Author:** Carlos Leguizamon Guillaumet

---

## Context

The project uses DuckDB as the development warehouse during weeks 5-15. DuckDB is an embedded library without a built-in graphical interface — it runs as a Python process or via CLI. For exploratory queries, schema inspection, and data validation during development, a SQL client is needed.

Multiple options exist: DBeaver Community, DuckDB CLI, VS Code SQLTools extension, and MotherDuck web UI.

## Decision

Use DBeaver Community as the primary SQL client for DuckDB exploration. Install DBeaver on Windows (host OS) and connect to DuckDB files stored in WSL via the `\\wsl$\` path.

## Rationale

- DBeaver is free, open-source, and cross-platform.
- The same client supports multiple warehouse backends (Snowflake, BigQuery, Postgres), making it a portable choice if the project migrates away from DuckDB in the future.
- Graphical schema explorer accelerates debugging during dbt model development.
- DuckDB CLI is faster for one-off queries but lacks visual table inspection, which slows down validation of joins and aggregations.
- MotherDuck requires uploading data to the cloud, which contradicts the local-first development principle of this project.

## Consequences

**Positive:**
- One tool covers DuckDB today and other warehouses if the project migrates in the future.
- Visual schema exploration speeds up dbt model debugging.
- Free, no vendor lock-in.

**Negative:**
- DBeaver is a Java application, slower to start than CLI.
- Requires running on Windows host with cross-OS file path access to WSL files.

## Revisit when

- A team-based workflow is added that requires a centralized SQL editor.
- Migration to a different warehouse with poor DBeaver support.
- Performance issues on Windows/WSL bridge become blockers.