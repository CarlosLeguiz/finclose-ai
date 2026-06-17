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
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator


# Default arguments applied to all tasks in this DAG.
# These can be overridden per-task if needed.
default_args = {
    "owner": "carlos",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,           # No retries in this initial version (Sesión 2 adds them)
    "retry_delay": timedelta(minutes=5),
}

# Path to the FinClose project root, as mounted inside the container
PROJECT_ROOT = "/opt/finclose-ai"


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

    # Task 3: Build dbt models (run + test combined)
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"cd {PROJECT_ROOT}/dbt_project && "
            "dbt build --profiles-dir ."
        ),
        doc_md="""
        ### dbt build

        Runs all 14 dbt models (7 staging, 2 intermediate, 5 marts) in
        topological order, then executes the 92 data tests. Stops if any
        test fails.
        """,
    )

    # Task 4: Placeholder for success notification (will be enriched in Sesión 2)
    notify_success = EmptyOperator(
        task_id="notify_success",
        doc_md="""
        ### Success notification

        Placeholder task. In Sesión 2 this will send a notification to
        Slack/email with a summary of the run (row counts, test results,
        execution time).
        """,
    )

    # Define the task dependencies (the DAG itself)
    generate_data >> load_to_duckdb >> dbt_build >> notify_success