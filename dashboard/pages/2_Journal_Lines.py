"""Journal Lines Explorer page — line-level drilldown of posted entries."""

import plotly.express as px
import streamlit as st

from utils.data import run_query

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Journal Lines - FinClose AI",
    layout="wide",
)

st.title("Journal Lines Explorer")
st.caption("Line-level detail of all posted journal entries")


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_journal_lines():
    """Load fct_journal_lines (already filtered to Posted)."""
    return run_query("""
        SELECT
            je_line_id,
            je_id,
            entry_date,
            period_id,
            period_year,
            period_month,
            period_quarter,
            account_code,
            account_name,
            account_type,
            cost_center_code,
            cost_center_name,
            department,
            debit_amount,
            credit_amount,
            net_amount,
            signed_amount,
            amount_abs,
            currency,
            source_system,
            line_description
        FROM main.fct_journal_lines
    """)


df = load_journal_lines()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

available_years = sorted(df["period_year"].dropna().unique().tolist())
selected_year = st.sidebar.selectbox(
    "Year", options=available_years, index=len(available_years) - 1
)

available_quarters = sorted(df["period_quarter"].dropna().unique().tolist())
selected_quarters = st.sidebar.multiselect(
    "Quarter", options=available_quarters, default=available_quarters
)

available_account_types = sorted(df["account_type"].dropna().unique().tolist())
selected_account_types = st.sidebar.multiselect(
    "Account Type",
    options=available_account_types,
    default=available_account_types,
)

available_departments = sorted(df["department"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Department",
    options=available_departments,
    default=available_departments,
)

available_sources = sorted(df["source_system"].dropna().unique().tolist())
selected_sources = st.sidebar.multiselect(
    "Source System",
    options=available_sources,
    default=available_sources,
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df[
    (df["period_year"] == selected_year)
    & (df["period_quarter"].isin(selected_quarters))
    & (df["account_type"].isin(selected_account_types))
    & (df["department"].isin(selected_departments) | df["department"].isna())
    & (df["source_system"].isin(selected_sources))
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
total_lines = len(filtered)
total_entries = filtered["je_id"].nunique()
total_debit = filtered["debit_amount"].sum()
total_credit = filtered["credit_amount"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Lines", f"{total_lines:,}")
col2.metric("Unique Entries", f"{total_entries:,}")
col3.metric("Total Debit (ARS)", f"${total_debit:,.0f}")
col4.metric("Total Credit (ARS)", f"${total_credit:,.0f}")

# Double-entry sanity check
diff = abs(total_debit - total_credit)
if diff < 0.01:
    st.success(f"Double-entry preserved: debit and credit balance to within ${diff:,.2f}")
else:
    st.error(f"Debit/Credit imbalance detected: ${diff:,.2f}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Chart: Activity volume by department
# ---------------------------------------------------------------------------
st.subheader("Activity volume by department")

dept_volume = (
    filtered.dropna(subset=["department"])
    .groupby("department", as_index=False)["amount_abs"]
    .sum()
    .sort_values("amount_abs", ascending=False)
)

fig = px.bar(
    dept_volume,
    x="department",
    y="amount_abs",
    labels={"amount_abs": "Total activity (ARS)", "department": "Department"},
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Detail table
# ---------------------------------------------------------------------------
st.subheader(f"Detail ({total_lines:,} lines)")

display_cols = [
    "entry_date",
    "je_id",
    "period_id",
    "account_code",
    "account_name",
    "account_type",
    "cost_center_code",
    "department",
    "debit_amount",
    "credit_amount",
    "net_amount",
    "currency",
    "source_system",
]

st.dataframe(
    filtered[display_cols].sort_values("entry_date", ascending=False),
    use_container_width=True,
    height=500,
)

# Export option
st.download_button(
    label="Download filtered data as CSV",
    data=filtered[display_cols].to_csv(index=False).encode("utf-8"),
    file_name=f"journal_lines_{selected_year}.csv",
    mime="text/csv",
)