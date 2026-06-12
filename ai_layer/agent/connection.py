"""Database connection layer for the LangChain SQL agent.

Provides a read-only SQLDatabase wrapper around the DuckDB warehouse,
exposing only the mart tables so the agent cannot query staging or raw.
"""

from pathlib import Path

from langchain_community.utilities import SQLDatabase

DUCKDB_PATH = Path(__file__).resolve().parents[2] / "data" / "finclose.duckdb"

# Only marts are exposed to the agent.
# Staging, intermediate, and raw tables are kept out of scope to:
#   1. Reduce token usage (schema sent to the LLM)
#   2. Force the agent to use the curated, tested data layer
#   3. Avoid the agent accidentally querying unprocessed data
ALLOWED_TABLES = [
    "dim_accounts",
    "dim_cost_centers",
    "dim_periods",
    "fct_budget_vs_actual",
    "fct_journal_lines",
]


def get_database() -> SQLDatabase:
    """Return a read-only SQLDatabase wrapper around the DuckDB warehouse.

    The agent will only see the tables listed in ALLOWED_TABLES.
    Sample rows (3) are included so the LLM understands data shape.
    """
    return SQLDatabase.from_uri(
        f"duckdb:///{DUCKDB_PATH}",
        include_tables=ALLOWED_TABLES,
        sample_rows_in_table_info=3,
    )


if __name__ == "__main__":
    # Manual test when running this file directly
    db = get_database()
    print("Tables visible to the agent:")
    for table in db.get_usable_table_names():
        print(f"  - {table}")
    print("\nSample of table info sent to LLM (truncated):")
    print(db.get_table_info()[:500])