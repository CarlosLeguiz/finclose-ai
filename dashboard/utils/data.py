"""Data access layer for the Streamlit dashboard.

Centralizes the connection to DuckDB and provides cached query functions.
All Streamlit pages should import from here instead of opening their own
DuckDB connections.
"""

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

DUCKDB_PATH = Path(__file__).resolve().parents[2] / "data" / "finclose.duckdb"


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a read-only DuckDB connection, cached across reruns.

    @st.cache_resource ensures we don't open a new connection on every
    user interaction (which would be expensive and would conflict with
    other readers).
    """
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)


@st.cache_data(ttl=300)
def run_query(query: str) -> pd.DataFrame:
    """Execute a SQL query and return the result as a pandas DataFrame.

    Results are cached for 5 minutes (ttl=300) to avoid re-running the
    same query repeatedly when the user interacts with widgets.
    """
    con = get_connection()
    return con.execute(query).fetchdf()