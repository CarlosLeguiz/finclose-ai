-- Mart fact: journal lines at line-level granularity, ready for consumption
-- Built on int_journal_lines_enriched, filtered to Posted entries only.
-- Adds derived analytical columns:
--   - net_amount: debit - credit (sign follows accounting convention)
--   - signed_amount: net_amount adjusted by account type so that
--     positive always means "increase" regardless of account type.
--     Asset/Expense: +debit / -credit
--     Liability/Equity/Revenue: +credit / -debit
--   - amount_abs: absolute value of the movement, useful for activity volume
-- Granularity: one row per journal line. Use this mart for detail-level
-- drilldowns; use fct_budget_vs_actual for aggregated variance analysis.

WITH enriched AS (
    SELECT * FROM {{ ref('int_journal_lines_enriched') }}
),

posted AS (
    SELECT *
    FROM enriched
    WHERE entry_status = 'Posted'
)

SELECT
    -- Keys
    je_line_id,
    je_id,
    line_number,
    account_id,
    cost_center_id,
    period_id,

    -- Dates and time context
    entry_date,
    period_year,
    period_month,
    period_quarter,
    period_is_closed,
    entry_status,
    source_system,
    created_by,

    -- Descriptive labels (denormalized from dimensions)
    account_code,
    account_name,
    account_type,
    cost_center_code,
    cost_center_name,
    department,

    -- Amounts
    debit_amount,
    credit_amount,
    currency,
    line_description,
    entry_description,

    -- Derived analytical columns
    debit_amount - credit_amount AS net_amount,

    CASE
        WHEN account_type IN ('Asset', 'Expense')
            THEN debit_amount - credit_amount
        WHEN account_type IN ('Liability', 'Equity', 'Revenue')
            THEN credit_amount - debit_amount
    END AS signed_amount,

    debit_amount + credit_amount AS amount_abs

FROM posted