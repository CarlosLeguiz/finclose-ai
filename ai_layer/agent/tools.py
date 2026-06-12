"""High-level tools that wrap the SQL agent for specific FP&A workflows.

These functions expose strongly-typed entry points (e.g. by account_id and
period_id) instead of free-form natural language. They are intended to be
called from the Streamlit dashboard when a user clicks "Explain this variance"
on a specific row, providing predictable cost and behavior.
"""

from ai_layer.agent.sql_agent import ask


def explain_variance(
    account_id: str,
    period_id: str,
    verbose: bool = False,
) -> str:
    """Generate an executive-style explanation of a specific variance.

    The function constructs a focused, deterministic question for the agent
    and returns its narrative analysis. Use this from Streamlit when the
    user requests an explanation of a single (account, period) intersection.

    Args:
        account_id: e.g. 'ACC042'
        period_id: e.g. '2026-03'
        verbose: prints intermediate reasoning steps if True (dev only)

    Returns:
        A multi-line markdown-friendly string with the agent's analysis.
    """
    question = f"""
Provide a concise executive analysis of the budget variance for account
{account_id} in period {period_id}.

Your response MUST follow this EXACT markdown structure:

**Account:** [account_name] ([account_type])
**Cost Center:** [cost_center_name] ([department])
**Period:** [period_label]

| Metric | Value |
|---|---|
| Actual Amount | ARS X,XXX,XXX.XX |
| Budgeted Amount | ARS X,XXX,XXX.XX |
| Variance | ARS X,XXX,XXX.XX |
| Variance % | XX.XX% |

**Assessment:** [favorable | unfavorable] variance (overperformed/underspent/...).

**Business Interpretation:** [2-3 sentences explaining what this likely means
from a business standpoint, and what a CFO might want to investigate]

Do not deviate from this structure. Do not add preamble. Do not add closing
remarks. Just the structured analysis.
""".strip()

    return ask(question, verbose=verbose)


def summarize_top_variances(
    period_id: str,
    top_n: int = 5,
    verbose: bool = False,
) -> str:
    """Generate an executive summary of the largest variances in a period.

    Args:
        period_id: e.g. '2026-03'
        top_n: how many top variances to include in the summary (default 5)
        verbose: prints intermediate reasoning steps if True (dev only)

    Returns:
        A multi-line summary covering the top N variances of the period.
    """
    question = f"""
Provide an executive summary of the top {top_n} largest budget variances
(by absolute value) for period {period_id}.

Filter to Revenue and Expense accounts only.

For each variance, briefly state:
- Account name and type
- Variance amount (ARS) and percentage
- Whether it's favorable or unfavorable per the account type rules

Close with a 2-line summary of the overall picture: which areas drove the
biggest deviations, and whether the period leans favorable or unfavorable
overall.

Keep the total response under 400 words.
""".strip()

    return ask(question, verbose=verbose)


if __name__ == "__main__":
    # Manual smoke test
    print("=" * 70)
    print("TEST 1: explain_variance")
    print("=" * 70)
    result = explain_variance("ACC042", "2026-03")
    print(result)

    print("\n" + "=" * 70)
    print("TEST 2: summarize_top_variances")
    print("=" * 70)
    result = summarize_top_variances("2026-03", top_n=3)
    print(result)