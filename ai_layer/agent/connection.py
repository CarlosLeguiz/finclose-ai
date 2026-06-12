"""Database connection layer for the LangChain SQL agent.

Provides a SQLDatabase wrapper around the DuckDB warehouse, exposing only
the mart tables. Each call to get_database() creates a fresh engine; the
caller is responsible for disposing it after use to avoid lingering
connections that conflict with other DuckDB clients.
"""

from pathlib import Path

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

DUCKDB_PATH = Path(__file__).resolve().parents[2] / "data" / "finclose.duckdb"

ALLOWED_TABLES = [
    "dim_accounts",
    "dim_cost_centers",
    "dim_periods",
    "fct_budget_vs_actual",
    "fct_journal_lines",
]


def get_database() -> SQLDatabase:
    """Return a SQLDatabase wrapper. Uses read_only mode via duckdb-engine
    config so it can coexist with the Streamlit dashboard's connection.
    """
    engine = create_engine(
        f"duckdb:///{DUCKDB_PATH}",
        connect_args={"read_only": True},
    )
    return SQLDatabase(
        engine=engine,
        include_tables=ALLOWED_TABLES,
        sample_rows_in_table_info=3,
    )


if __name__ == "__main__":
    db = get_database()
    print("Tables visible to the agent:")
    for table in db.get_usable_table_names():
        print(f"  - {table}")