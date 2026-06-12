"""AI Insights page - executive summaries and free-form Q&A powered by the
FinClose AI SQL agent.

This page exposes two AI-powered workflows:
1. Period summary: top variances of a selected period, narrated by the agent.
2. Free-form chat: ask any question about the marts in natural language.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from utils.data import run_query
from ai_layer.agent.sql_agent import ask
from ai_layer.agent.tools import summarize_top_variances


st.set_page_config(
    page_title="AI Insights - FinClose AI",
    layout="wide",
)

st.title("AI Insights")
st.caption("Executive summaries and free-form questions powered by AI")

# ---------------------------------------------------------------------------
# Section 1: Period summary
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Period summary")
st.caption("Get an executive summary of the largest variances in a period.")

# Load available periods from the warehouse
periods_df = run_query("""
    SELECT period_id, period_label
    FROM main.dim_periods
    ORDER BY period_id DESC
""")

col_a, col_b, col_c = st.columns([2, 1, 1])

with col_a:
    period_label_to_id = dict(zip(periods_df["period_label"], periods_df["period_id"]))
    selected_period_label = st.selectbox(
        "Period",
        options=periods_df["period_label"].tolist(),
        index=0,
    )
    selected_period_id = period_label_to_id[selected_period_label]

with col_b:
    top_n = st.number_input("Top N variances", min_value=3, max_value=10, value=5)

with col_c:
    st.write("")
    st.write("")
    summarize_clicked = st.button("Generate Summary", use_container_width=True)

if summarize_clicked:
    with st.spinner("Generating period summary..."):
        try:
            summary = summarize_top_variances(
                period_id=selected_period_id,
                top_n=top_n,
            )
            st.markdown(summary)
        except Exception as e:
            st.error(f"Error generating summary: {e}")

# ---------------------------------------------------------------------------
# Section 2: Free-form chat
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Ask the agent")
st.caption(
    "Ask any question about the data in natural language. "
    "The agent has read-only access to the 5 mart tables (dim_accounts, "
    "dim_cost_centers, dim_periods, fct_budget_vs_actual, fct_journal_lines)."
)

# Examples to inspire users
with st.expander("Example questions"):
    st.markdown("""
    - What is the total revenue for Q1 2026?
    - Which department has the largest expense variance in March 2026?
    - Compare actual vs budget for the Marketing department in 2026.
    - List the top 5 accounts with the most journal line activity this year.
    - What is the average monthly expense by department?
    """)

user_question = st.text_area(
    "Your question",
    placeholder="e.g. What were the top 3 expense accounts in February 2026?",
    height=100,
)

ask_clicked = st.button("Ask", type="primary")

if ask_clicked and user_question.strip():
    with st.spinner("Thinking..."):
        try:
            answer = ask(user_question.strip())
            st.markdown(answer)
        except Exception as e:
            st.error(f"Error: {e}")
elif ask_clicked:
    st.warning("Please enter a question.")