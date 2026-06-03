"""Load generated CSV files into DuckDB as raw tables.

This script is the bridge between the data generator (Python)
and the dbt transformation layer (SQL). It creates/opens a DuckDB
database file and loads each CSV from data/raw/ as a raw_* table.

Run with:
    poetry run python -m data_generator.load_to_duckdb
"""

from pathlib import Path

import duckdb


# Mapping of CSV files to raw table names
CSV_TO_TABLE = {
    "dim_accounts.csv":           "raw_accounts",
    "dim_cost_centers.csv":       "raw_cost_centers",
    "dim_periods.csv":             "raw_periods",
    "dim_exchange_rates.csv":     "raw_exchange_rates",
    "fact_journal_entries.csv":   "raw_journal_entries",
    "fact_journal_lines.csv":     "raw_journal_lines",
    "fact_budgets.csv":            "raw_budgets",
}


def load_csvs_to_duckdb(
    csv_dir: Path = Path("data/raw"),
    duckdb_path: Path = Path("data/finclose.duckdb"),
) -> None:
    """Load all CSV files into DuckDB as raw_* tables.

    Args:
        csv_dir: directory containing the source CSVs.
        duckdb_path: destination DuckDB database file (created if not exists).
    """
    # Ensure parent directory exists
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB (creates file if missing)
    conn = duckdb.connect(str(duckdb_path))

    for csv_file, table_name in CSV_TO_TABLE.items():
        csv_path = csv_dir / csv_file

        if not csv_path.exists():
            print(f"⚠ Skipping {csv_file}: file not found")
            continue

        # Drop existing table if any (idempotent reload)
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Load CSV into the table
        conn.execute(
            f"CREATE TABLE {table_name} AS "
            f"SELECT * FROM read_csv_auto('{csv_path}')"
        )

        # Count rows loaded
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Loaded {row_count:>6} rows → {table_name}")

    conn.close()
    print(f"\nDatabase ready at: {duckdb_path}")


if __name__ == "__main__":
    load_csvs_to_duckdb()