"""FinClose AI Dashboard — main entry point (Summary / KPIs)."""

import streamlit as st

from utils.data import run_query

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FinClose AI",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("FinClose AI")
st.caption("Automated Financial Close & Variance Analysis Platform")

st.markdown("---")

# ---------------------------------------------------------------------------
# Top KPIs
# ---------------------------------------------------------------------------
st.subheader("Pipeline Overview")

# Query for high-level metrics
kpi_df = run_query("""
    SELECT
        (SELECT COUNT(*) FROM main.fct_journal_lines) AS total_lines,
        (SELECT COUNT(DISTINCT je_id) FROM main.fct_journal_lines) AS total_entries,
        (SELECT COUNT(*) FROM main.dim_accounts WHERE is_active = TRUE) AS active_accounts,
        (SELECT COUNT(*) FROM main.dim_cost_centers WHERE is_active = TRUE) AS active_cost_centers,
        (SELECT COUNT(*) FROM main.dim_periods) AS total_periods,
        (SELECT SUM(debit_amount) FROM main.fct_journal_lines) AS total_volume
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Journal Lines", f"{kpi_df['total_lines'][0]:,}")
    st.metric("Journal Entries", f"{kpi_df['total_entries'][0]:,}")

with col2:
    st.metric("Active Accounts", kpi_df['active_accounts'][0])
    st.metric("Active Cost Centers", kpi_df['active_cost_centers'][0])

with col3:
    st.metric("Periods", kpi_df['total_periods'][0])
    st.metric(
        "Total Volume (ARS)",
        f"${kpi_df['total_volume'][0]:,.0f}"
    )

with col4:
    st.metric("dbt Models", 14)
    st.metric("Data Tests", 92)

st.markdown("---")
st.info("Use the sidebar to navigate to detailed views.")