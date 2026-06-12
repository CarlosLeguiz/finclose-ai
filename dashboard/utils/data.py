"""Data access layer for the Streamlit dashboard.

Uses SQLAlchemy + duckdb-engine to share the same connection pool with
the AI agent layer (ai_layer/agent/connection.py). Both must use the same
driver to avoid "different configuration" conflicts on the same DuckDB file.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

DUCKDB_PATH = Path(__file__).resolve().parents[2] / "data" / "finclose.duckdb"


@st.cache_resource
def get_engine():
    """Return a shared SQLAlchemy engine for the DuckDB warehouse.

    Cached across reruns via @st.cache_resource so we don't open multiple
    connections to the same file (which causes DuckDB to error out).
    """
    return create_engine(
        f"duckdb:///{DUCKDB_PATH}",
        connect_args={"read_only": True},
    )


@st.cache_data(ttl=300)
def run_query(query: str) -> pd.DataFrame:
    """Execute a SQL query and return the result as a pandas DataFrame.

    Results cached 5 minutes to avoid redundant queries on widget interactions.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)