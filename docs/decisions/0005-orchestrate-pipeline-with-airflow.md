# 0005 - Orchestrate pipeline with Airflow on Docker Compose

**Date:** 2026-06-17
**Status:** Accepted
**Author:** Carlos Leguizamon Guillaumet

## Context

Until this point, the FinClose AI pipeline ran via manual commands:

```bash
python -m data_generator.main
python -m data_generator.load_to_duckdb
cd dbt_project && dbt build
```

This works for development but does not match production patterns: real
financial close pipelines run on schedules, retry on transient failures,
alert on incidents, and provide auditable run history. Showing the
pipeline running as scripts undersells the engineering maturity of the
project for a Data Engineer portfolio.

The decision was to introduce an orchestrator that handles scheduling,
dependencies, retries, and observability without requiring a cloud account.

## Decision

Use Apache Airflow 3.1.1, deployed locally via Docker Compose, with the
following design:

### Architecture
- One Docker Compose stack with 7 services: postgres (metadata DB),
  redis (Celery broker), scheduler, dag-processor, triggerer, apiserver,
  and worker.
- A custom Airflow image (`airflow/Dockerfile`) extends
  `apache/airflow:3.1.1` with Poetry, dbt-core 1.11.11, dbt-duckdb 1.10.1,
  and the project's Python dependencies. This avoids the brittleness of
  `_PIP_ADDITIONAL_REQUIREMENTS`, which is explicitly discouraged by
  the official documentation for non-trivial use cases.
- The project root is mounted into the container at `/opt/finclose-ai`
  so tasks have full access to data, dbt models, and Python modules.

### DAG design
- One DAG: `finclose_pipeline` with five sequential tasks:
  1. `generate_synthetic_data`
  2. `load_to_duckdb`
  3. `dbt_run` (materialize models only)
  4. `dbt_test` (data quality validation only)
  5. `notify_success` (placeholder for Slack/email)
- `dbt_run` and `dbt_test` are kept separate (rather than combined as
  `dbt build`) so failures isolate cleanly: a red `dbt_test` with a
  green `dbt_run` immediately indicates data quality issues, not
  modeling errors.
- Schedule `@monthly` to simulate financial closing cadence.

### Error handling
- `retries: 2` and `retry_delay: 2 min` on all tasks (configured in
  `default_args`).
- `execution_timeout: 15 min` to kill hung tasks.
- `on_failure_callback`: a Python function that writes structured
  incident records to `logs/airflow_failures.log`. In production this
  would post to Slack/PagerDuty/email.

## Alternatives considered

### `_PIP_ADDITIONAL_REQUIREMENTS`
Airflow supports injecting additional pip requirements at startup via
this environment variable. Rejected because the documentation explicitly
warns against using it outside of quick checks; for any persistent setup
the recommendation is to build a custom image.

### Astronomer Cosmos
A modern alternative that natively integrates dbt and Airflow. Rejected
for this portfolio iteration because it adds dependency surface and
hides the dbt commands behind abstractions. Using `BashOperator` keeps
the DAG transparent and easy to defend in interviews. Cosmos remains
a candidate for a future iteration.

### Managed Airflow (MWAA, Composer)
Production-grade but costs money and adds 5+ hours of cloud setup
without proportional learning value. Local Docker Compose is fully
defensible: "I deployed Airflow locally with Docker Compose; for
production I would migrate to MWAA on AWS or Composer on GCP."

### Single dbt task
The original design had a single `dbt_build` task. Rejected after
implementation because it conflates two distinct phases (materialization
and testing) and hurts observability. Splitting into `dbt_run` and
`dbt_test` aligns with how data engineers debug pipelines in production.

## Consequences

### Positive
- Pipeline now runs on a schedule with full observability via the
  Airflow UI.
- Retries and timeouts handle transient failures automatically.
- Failure callbacks provide an extensibility hook for real
  notifications.
- Granular dbt tasks enable rapid diagnosis of failures (modeling vs
  data quality).
- Setup is portable: anyone with Docker can clone the repo and run
  `docker compose up -d` to reproduce the environment.

### Negative
- Increased complexity: 7 Docker services to manage, custom image to
  rebuild on dependency changes.
- Requires Docker Desktop and WSL2 integration on Windows, which has
  occasional connectivity issues.
- DuckDB file lock contention: only one process can write at a time,
  so the Streamlit dashboard must be stopped before running the DAG
  manually (or vice versa).

### Mitigated
- The custom Docker image is reproducible: `docker compose build`
  guarantees the same environment across runs.
- All Airflow runtime artifacts (logs, configs, `.env`) are gitignored
  to keep the repo clean.