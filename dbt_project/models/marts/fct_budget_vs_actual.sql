-- Mart model: budget vs actual variance analysis
-- FULL OUTER JOIN between int_actuals_full and stg_budgets (active only)
-- at the (account_id, cost_center_id, period_id) grain.
-- Preserves actuals without budget and budgets without actual.
-- Computes variance (actual - budget) and variance_pct, with NULL guard
-- against division by zero. Central fact table for the FP&A dashboard.
--
-- Uses int_actuals_full.signed_amount (sign-normalized per account_type)
-- so that variance comparison vs budget is mathematically meaningful.

WITH actuals AS (
    SELECT * FROM {{ ref('int_actuals_full') }}
),

budgets AS (
    SELECT
        account_id,
        cost_center_id,
        period_id,
        budgeted_amount
    FROM {{ ref('stg_budgets') }}
    WHERE is_active = TRUE
),

joined AS (
    SELECT
        COALESCE(a.account_id, b.account_id) AS account_id,
        COALESCE(a.cost_center_id, b.cost_center_id) AS cost_center_id,
        COALESCE(a.period_id, b.period_id) AS period_id,
        COALESCE(a.signed_amount, 0) AS actual_amount,
        COALESCE(b.budgeted_amount, 0) AS budgeted_amount
    FROM actuals a
    FULL OUTER JOIN budgets b
        ON a.account_id = b.account_id
        AND a.cost_center_id = b.cost_center_id
        AND a.period_id = b.period_id
)

SELECT
    account_id,
    cost_center_id,
    period_id,
    actual_amount,
    budgeted_amount,
    actual_amount - budgeted_amount AS variance,
    CASE
        WHEN budgeted_amount = 0 THEN NULL
        ELSE ROUND((actual_amount - budgeted_amount) / budgeted_amount * 100, 2)
    END AS variance_pct
FROM joined