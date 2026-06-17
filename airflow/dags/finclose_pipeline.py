"""FinClose AI - End-to-end pipeline orchestration.

This DAG runs the complete data pipeline:
1. Generate synthetic accounting data with the data_generator package
2. Load the generated CSVs into DuckDB
3. Build the dbt models (staging -> intermediate -> marts)
4. Run dbt tests to validate data quality
5. Log a success notification

The pipeline simulates a monthly financial close process. Tasks run
sequentially since each depends on the previous one. Failures stop the
pipeline immediately, preventing downstream tasks from running on bad data.

Each task has automatic retries on transient failures and a timeout to
prevent hung executions. A failure callback writes structured logs to a
file for incident review.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator


# Path to the FinClose project root, as mounted inside the container
PROJECT_ROOT = "/opt/finclose-ai"

# Path for the failure incident log (inside the container; mapped to host)
FAILURE_LOG_PATH = f"{PROJECT_ROOT}/logs/airflow_failures.log"


def log_task_failure(context: dict) -> None:
    """Failure callback: append a structured incident record to a log file.

    In production this would post to Slack, PagerDuty, or send an email.
    For portfolio purposes, we write to a local log file that demonstrates
    the integration pattern.

    The `context` dict is Airflow's standard task context with fields like
    task_instance, dag_run, exception, etc.
    """
    ti = context["task_instance"]
    dag_run = context["dag_run"]
    exception = context.get("exception")

    log_line = (
        f"{datetime.utcnow().isoformat()}Z | "
        f"DAG={ti.dag_id} | "
        f"TASK={ti.task_id} | "
        f"RUN_ID={dag_run.run_id} | "
        f"TRY={ti.try_number} | "
        f"EXCEPTION={exception}\n"
    )

    # Ensure the logs directory exists before writing
    Path(FAILURE_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(FAILURE_LOG_PATH, "a") as f:
        f.write(log_line)

    logging.error(f"Task failed: {ti.task_id} on run {dag_run.run_id}")


# Default arguments applied to all tasks in this DAG.
# These can be overridden per-task if needed.
default_args = {
    "owner": "carlos",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,                           # Retry failed tasks up to 2 times
    "retry_delay": timedelta(minutes=2),    # Wait 2 minutes between retries
    "execution_timeout": timedelta(minutes=15),  # Kill task if > 15 min
    "on_failure_callback": log_task_failure,     # Log failures to file
}


with DAG(
    dag_id="finclose_pipeline",
    description="End-to-end orchestration of the FinClose AI data pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",     # Simulates a monthly closing process
    catchup=False,           # Do NOT backfill historical runs
    tags=["finclose", "fp&a", "dbt"],
) as dag:

    # Task 1: Generate synthetic accounting data (CSVs)
    generate_data = BashOperator(
        task_id="generate_synthetic_data",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "python -m data_generator.main"
        ),
        doc_md="""
        ### Generate synthetic data

        Runs the `data_generator/main.py` module which produces 7 CSVs in
        `data/raw/`: dim_accounts, dim_cost_centers, dim_periods,
        dim_exchange_rates, fact_journal_entries, fact_journal_lines,
        and fact_budgets.

        The generator uses a fixed RANDOM_SEED for reproducibility.
        """,
    )

    # Task 2: Load the CSVs into DuckDB as raw_* tables
    load_to_duckdb = BashOperator(
        task_id="load_to_duckdb",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "python -m data_generator.load_to_duckdb"
        ),
        doc_md="""
        ### Load CSVs to DuckDB

        Reads the 7 CSVs from `data/raw/` and writes them as `raw_*` tables
        in `data/finclose.duckdb`. These tables are the sources for the
        dbt staging models.
        """,
    )

    # Task 3a: Run dbt models (materialize staging -> intermediate -> marts)
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_project && "
            "dbt run --profiles-dir ."
        ),
        doc_md="""
        ### dbt run

        Materializes all 14 dbt models in topological order:
        - 7 staging models (one-to-one with raw tables)
        - 2 intermediate models (with sign normalization and joins)
        - 5 mart models (consumed by dashboard and AI agent)

        This is the heavy step — separated from `dbt_test` so the user
        can rerun tests independently without rebuilding all materializations.
        """,
    )

    # Task 3b: Run dbt tests (data quality validation)
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_project && "
            "dbt test --profiles-dir ."
        ),
        doc_md="""
        ### dbt test

        Executes the 92 data tests:
        - Generic tests (unique, not_null, accepted_values, relationships)
          in _staging.yml and _marts.yml
        - 3 custom singular tests (journal entries balanced, cost center
          assignment rules, actuals aggregation integrity)

        If any test fails, the pipeline stops here. The notify_success
        task will not be executed, and the failure callback will fire.
        """,
    )

    # Task 4: Placeholder for success notification (will be enriched in Sesión 2)
    notify_success = EmptyOperator(
        task_id="notify_success",
        doc_md="""
        ### Success notification

        Placeholder task. In a production deployment this would send a
        notification to Slack/email with a summary of the run.
        """,
    )

    # Define the task dependencies (the DAG itself)
    generate_data >> load_to_duckdb >> dbt_run >> dbt_test >> notify_success