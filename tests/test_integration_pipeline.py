"""Integration test: end-to-end pipeline validation.

Runs the full pipeline in a temporary directory:
1. Generate synthetic data (CSVs)
2. Load to DuckDB
3. Run dbt models (dbt run)
4. Run dbt tests (dbt test)
5. Validate marts have expected data

Marked as 'integration' to exclude from default pytest run.
Execute with: poetry run pytest -m integration
"""
import os
import subprocess
from pathlib import Path

import duckdb
import pytest

from data_generator.dimensions import (
    generate_accounts,
    generate_cost_centers,
    generate_exchange_rates,
    generate_periods,
)
from data_generator.facts import (
    generate_budgets,
    generate_journal_entries,
    generate_journal_lines,
)
from data_generator.load_to_duckdb import load_csvs_to_duckdb
from data_generator.persistence import save_to_csv


PROJECT_ROOT = Path(__file__).parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"


@pytest.mark.integration
def test_full_pipeline_end_to_end(tmp_path: Path) -> None:
    """End-to-end test: generate -> load -> dbt run -> dbt test -> validate."""

    # Step 1: Generate synthetic data into temp directory
    csv_dir = tmp_path / "data" / "raw"
    csv_dir.mkdir(parents=True)

    accounts = generate_accounts()
    cost_centers = generate_cost_centers()
    periods = generate_periods()
    exchange_rates = generate_exchange_rates()
    journal_entries = generate_journal_entries(periods)
    journal_lines = generate_journal_lines(journal_entries, accounts, cost_centers)
    budgets = generate_budgets(accounts, cost_centers, periods)

    save_to_csv(accounts, csv_dir / "dim_accounts.csv")
    save_to_csv(cost_centers, csv_dir / "dim_cost_centers.csv")
    save_to_csv(periods, csv_dir / "dim_periods.csv")
    save_to_csv(exchange_rates, csv_dir / "dim_exchange_rates.csv")
    save_to_csv(journal_entries, csv_dir / "fact_journal_entries.csv")
    save_to_csv(journal_lines, csv_dir / "fact_journal_lines.csv")
    save_to_csv(budgets, csv_dir / "fact_budgets.csv")

    # Step 2: Load CSVs into DuckDB
    duckdb_path = tmp_path / "finclose.duckdb"
    load_csvs_to_duckdb(csv_dir=csv_dir, duckdb_path=duckdb_path)

    assert duckdb_path.exists(), "DuckDB file was not created"

    # Step 3: Run dbt with env var pointing to temp DB
    env = os.environ.copy()
    env["DBT_DUCKDB_PATH"] = str(duckdb_path)

    dbt_run = subprocess.run(
        ["poetry", "run", "dbt", "run", "--profiles-dir", "."],
        cwd=DBT_PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    assert dbt_run.returncode == 0, f"dbt run failed:\n{dbt_run.stdout}\n{dbt_run.stderr}"

    # Step 4: Run dbt tests
    dbt_test = subprocess.run(
        ["poetry", "run", "dbt", "test", "--profiles-dir", "."],
        cwd=DBT_PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    assert dbt_test.returncode == 0, f"dbt test failed:\n{dbt_test.stdout}\n{dbt_test.stderr}"

    # Step 5: Validate marts have expected data
    conn = duckdb.connect(str(duckdb_path), read_only=True)

    # dim_accounts: should have 80 accounts
    accounts_count = conn.execute("SELECT COUNT(*) FROM dim_accounts").fetchone()[0]
    assert accounts_count == 80, f"Expected 80 accounts, got {accounts_count}"

    # fct_journal_lines: should have substantial data (>10k rows)
    lines_count = conn.execute("SELECT COUNT(*) FROM fct_journal_lines").fetchone()[0]
    assert lines_count > 10_000, f"Expected >10k journal lines, got {lines_count}"

    # fct_budget_vs_actual: should have rows, all with non-null account_id
    variance_rows = conn.execute(
        "SELECT COUNT(*) FROM fct_budget_vs_actual WHERE account_id IS NULL"
    ).fetchone()[0]
    assert variance_rows == 0, f"Found {variance_rows} rows with NULL account_id in variance mart"

    total_variance_rows = conn.execute("SELECT COUNT(*) FROM fct_budget_vs_actual").fetchone()[0]
    assert total_variance_rows > 0, "fct_budget_vs_actual is empty"

    conn.close()