"""Variance Analysis page — actuals vs budget by account/cost center/period."""

import plotly.express as px
import streamlit as st

from utils.data import run_query

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Variance Analysis — FinClose AI",
    layout="wide",
)

st.title("Variance Analysis")
st.caption("Actuals vs Budget at account / cost center / period level")

# ---------------------------------------------------------------------------
# Load enriched data (single query with all joins)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_variance_data():
    """Load fct_budget_vs_actual enriched with dimension labels."""
    return run_query("""
        SELECT
            f.account_id,
            f.cost_center_id,
            f.period_id,
            a.account_code,
            a.account_name,
            a.account_type,
            a.is_balance_sheet,
            a.is_income_statement,
            cc.name AS cost_center_name,
            cc.department,
            cc.department_group,
            p.year,
            p.quarter,
            p.period_label,
            f.actual_amount,
            f.budgeted_amount,
            f.variance,
            f.variance_pct
        FROM main.fct_budget_vs_actual f
        LEFT JOIN main.dim_accounts a USING (account_id)
        LEFT JOIN main.dim_cost_centers cc USING (cost_center_id)
        LEFT JOIN main.dim_periods p USING (period_id)
    """)


df = load_variance_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

available_years = sorted(df["year"].dropna().unique().tolist())
selected_year = st.sidebar.selectbox("Year", options=available_years, index=len(available_years) - 1)

available_quarters = sorted(df["quarter"].dropna().unique().tolist())
selected_quarters = st.sidebar.multiselect("Quarter", options=available_quarters, default=available_quarters)

available_departments = sorted(df["department"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Department",
    options=available_departments,
    default=available_departments,
)

available_account_types = sorted(df["account_type"].dropna().unique().tolist())
selected_account_types = st.sidebar.multiselect(
    "Account Type",
    options=available_account_types,
    default=["Revenue", "Expense"],
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df[
    (df["year"] == selected_year)
    & (df["quarter"].isin(selected_quarters))
    & (df["department"].isin(selected_departments))
    & (df["account_type"].isin(selected_account_types))
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs row
# ---------------------------------------------------------------------------
total_actual = filtered["actual_amount"].sum()
total_budget = filtered["budgeted_amount"].sum()
total_variance = filtered["variance"].sum()
utilization = (total_actual / total_budget * 100) if total_budget != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Actual (ARS)", f"${total_actual:,.0f}")
col2.metric("Total Budget (ARS)", f"${total_budget:,.0f}")
col3.metric(
    "Variance (ARS)",
    f"${total_variance:,.0f}",
    delta=f"{(total_variance / total_budget * 100):.1f}%" if total_budget != 0 else None,
    delta_color="inverse",
)
col4.metric("Budget Utilization", f"{utilization:.1f}%")

st.markdown("---")

# ---------------------------------------------------------------------------
# Chart: Top 10 accounts by absolute variance
# ---------------------------------------------------------------------------
st.subheader("Top 10 accounts by absolute variance")

top10 = (
    filtered.groupby(["account_code", "account_name"], as_index=False)["variance"]
    .sum()
    .assign(abs_variance=lambda d: d["variance"].abs())
    .sort_values("abs_variance", ascending=False)
    .head(10)
)

fig = px.bar(
    top10,
    x="variance",
    y="account_name",
    orientation="h",
    color="variance",
    color_continuous_scale=["red", "lightgray", "green"],
    color_continuous_midpoint=0,
    labels={"variance": "Variance (ARS)", "account_name": ""},
    height=500,
)
fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Detail table
# ---------------------------------------------------------------------------
st.subheader("Detail")

display_cols = [
    "period_label",
    "account_code",
    "account_name",
    "account_type",
    "department",
    "cost_center_name",
    "actual_amount",
    "budgeted_amount",
    "variance",
    "variance_pct",
]

st.dataframe(
    filtered[display_cols].sort_values("variance", key=lambda s: s.abs(), ascending=False),
    use_container_width=True,
    height=400,
)