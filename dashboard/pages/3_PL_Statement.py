"""P&L Statement page — auto-generated Income Statement from posted journal lines."""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import run_query

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="P&L Statement - FinClose AI",
    layout="wide",
)

st.title("P&L Statement")
st.caption("Auto-generated Income Statement from posted journal entries")


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_pl_data():
    """Aggregate signed amounts by account_type and period for income statement accounts."""
    return run_query("""
        SELECT
            f.account_type,
            f.account_code,
            f.account_name,
            f.department,
            f.period_year,
            f.period_quarter,
            f.period_month,
            SUM(f.signed_amount) AS amount
        FROM main.fct_journal_lines f
        WHERE f.account_type IN ('Revenue', 'Expense')
        GROUP BY
            f.account_type,
            f.account_code,
            f.account_name,
            f.department,
            f.period_year,
            f.period_quarter,
            f.period_month
    """)


df = load_pl_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

available_years = sorted(df["period_year"].dropna().unique().tolist())
selected_year = st.sidebar.selectbox(
    "Year", options=available_years, index=len(available_years) - 1
)

period_granularity = st.sidebar.radio(
    "Granularity",
    options=["Annual", "Quarterly", "Monthly"],
)

available_departments = sorted(df["department"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Department",
    options=available_departments,
    default=available_departments,
    help="Filters Expense lines. Revenue is shown for all departments.",
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
# Revenue gets all departments (since revenue lines may not always have one).
# Expense filtered to selected departments.
revenue_df = df[
    (df["period_year"] == selected_year) & (df["account_type"] == "Revenue")
].copy()

expense_df = df[
    (df["period_year"] == selected_year)
    & (df["account_type"] == "Expense")
    & (df["department"].isin(selected_departments))
].copy()

filtered = pd.concat([revenue_df, expense_df], ignore_index=True)

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs row
# ---------------------------------------------------------------------------
total_revenue = revenue_df["amount"].sum()
total_expense = expense_df["amount"].sum()
net_result = total_revenue - total_expense
margin = (net_result / total_revenue * 100) if total_revenue != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue (ARS)", f"${total_revenue:,.0f}")
col2.metric("Total Expense (ARS)", f"${total_expense:,.0f}")
col3.metric(
    "Net Result (ARS)",
    f"${net_result:,.0f}",
    delta=f"{margin:.1f}% margin",
    delta_color="normal" if net_result >= 0 else "inverse",
)
col4.metric(
    "Expense / Revenue Ratio",
    f"{(total_expense / total_revenue * 100):.1f}%" if total_revenue != 0 else "N/A",
)

st.markdown("---")

# ---------------------------------------------------------------------------
# P&L statement (the centerpiece)
# ---------------------------------------------------------------------------
st.subheader(f"Income Statement - {selected_year}")

# Group by account_code + name to get totals per account
revenue_by_account = (
    revenue_df.groupby(["account_code", "account_name"], as_index=False)["amount"]
    .sum()
    .sort_values("amount", ascending=False)
)

expense_by_account = (
    expense_df.groupby(["account_code", "account_name"], as_index=False)["amount"]
    .sum()
    .sort_values("amount", ascending=False)
)

# Build the statement as a structured DataFrame
statement_rows = []

statement_rows.append({"Account": "REVENUE", "Amount": "", "is_header": True})
for _, row in revenue_by_account.iterrows():
    statement_rows.append({
        "Account": f"  {row['account_code']} - {row['account_name']}",
        "Amount": f"${row['amount']:,.0f}",
        "is_header": False,
    })
statement_rows.append({
    "Account": "  Total Revenue",
    "Amount": f"${total_revenue:,.0f}",
    "is_header": True,
})
statement_rows.append({"Account": "", "Amount": "", "is_header": False})

statement_rows.append({"Account": "EXPENSES", "Amount": "", "is_header": True})
for _, row in expense_by_account.iterrows():
    statement_rows.append({
        "Account": f"  {row['account_code']} - {row['account_name']}",
        "Amount": f"$({row['amount']:,.0f})",
        "is_header": False,
    })
statement_rows.append({
    "Account": "  Total Expenses",
    "Amount": f"$({total_expense:,.0f})",
    "is_header": True,
})
statement_rows.append({"Account": "", "Amount": "", "is_header": False})

statement_rows.append({
    "Account": "NET RESULT",
    "Amount": f"${net_result:,.0f}",
    "is_header": True,
})

pl_df = pd.DataFrame(statement_rows)[["Account", "Amount"]]
st.dataframe(pl_df, use_container_width=True, height=600, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Trend chart based on granularity
# ---------------------------------------------------------------------------
st.subheader(f"{period_granularity} trend")

if period_granularity == "Annual":
    trend = filtered.groupby("account_type", as_index=False)["amount"].sum()
    trend["period_label"] = str(selected_year)
elif period_granularity == "Quarterly":
    trend = filtered.groupby(["account_type", "period_quarter"], as_index=False)["amount"].sum()
    trend["period_label"] = "Q" + trend["period_quarter"].astype(str)
else:  # Monthly
    trend = filtered.groupby(["account_type", "period_month"], as_index=False)["amount"].sum()
    trend["period_label"] = trend["period_month"].apply(lambda m: f"{selected_year}-{m:02d}")

fig = px.bar(
    trend,
    x="period_label",
    y="amount",
    color="account_type",
    barmode="group",
    labels={"period_label": "Period", "amount": "Amount (ARS)", "account_type": "Type"},
    color_discrete_map={"Revenue": "#2ecc71", "Expense": "#e74c3c"},
    height=400,
)
st.plotly_chart(fig, use_container_width=True)