# 0004 - Normalize actual_amount sign in budget vs actual mart

**Date:** 2026-06-12
**Status:** Accepted
**Author:** Carlos Leguizamon Guillaumet

## Context

The `fct_budget_vs_actual` mart originally computed `actual_amount` as
`int_actuals_full.net_amount`, which is the raw accounting expression
`SUM(debit_amount) - SUM(credit_amount)`.

This convention produces opposite signs depending on account type:
- Positive for Asset and Expense accounts
- Negative for Liability, Equity, and Revenue accounts

Meanwhile, the budgeted amount in `stg_budgets.budgeted_amount` is always
stored as a positive value (a Revenue budget of "we expect to sell 500k"
is stored as +500,000).

The result was that `variance = actual - budget` was mathematically
inconsistent for non-Asset/Expense accounts: for a Revenue account with
real sales, the actual would be negative (e.g. -480,000) and the budget
positive (e.g. +500,000), producing a variance of -980,000 that conflated
two different sign conventions in the same formula.

This was discovered when the AI agent generated correct SQL but produced
incoherent interpretations of variances, with all Revenue accounts
appearing to be "overspending" because of the sign mismatch rather than
any real performance issue.

## Decision

Two coordinated changes were applied:

### 1. Add `signed_amount` to `int_actuals_full`

The intermediate model now exposes two amount representations:
- `net_amount` (existing): raw debit minus credit, retained for accounting
  audits and traceability.
- `signed_amount` (new): sign-normalized by account_type so that positive
  always means "increase" for the account.

For Asset/Expense accounts: `signed_amount = debit - credit`
For Liability/Equity/Revenue: `signed_amount = credit - debit`

This is the same normalization logic already applied in `fct_journal_lines`,
now also available at the aggregated level.

### 2. Update `fct_budget_vs_actual` to use `signed_amount`

The mart's `actual_amount` now sources from `int_actuals_full.signed_amount`
instead of `net_amount`. Variance computation against the always-positive
budget is now sign-consistent.

### 3. Recalibrate the data generator

In addition to the SQL changes, the synthetic data generator was rebalanced
to produce realistic debit/credit distributions across all 5 account types.
The previous configuration limited debits to Asset/Expense only and credits
to Asset/Liability/Revenue only, producing unidirectional movements that
masked the original bug.

New distributions in `data_generator/config.py`:
- `DEBIT_ACCOUNT_TYPE_WEIGHTS`: includes all 5 types, dominant in
  Expense (55%) and Asset (35%).
- `CREDIT_ACCOUNT_TYPE_WEIGHTS`: includes all 5 types, dominant in
  Revenue (35%) and Asset (30%).

## Consequences

### Positive
- `fct_budget_vs_actual.variance` is now mathematically meaningful
- AI agent and dashboard consume consistent, interpretable values
- Synthetic data reflects realistic accounting practice (Asset accounts
  with both debits and credits, etc.)
- `net_amount` is preserved as a separate column for auditing purposes
- All 92 dbt tests continue to pass without modification

### Trade-offs
- Users of `int_actuals_full` must now choose between `net_amount` and
  `signed_amount` based on their use case. This is documented in the
  model SQL comments and in the AI agent's system prompt.
- The mart values changed for all accounts with non-Debit normal balance.
  Any external system referencing previous numbers would need to be
  realigned.

### Mitigated
- The change is backwards-compatible at the schema level: `net_amount`
  remains available, only the mart's choice of source column changed.
- 106 dbt nodes (14 models + 92 tests) all pass after the refactor,
  confirming no regressions in data integrity or business rules.