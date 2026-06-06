-- Mart dimension: enriched chart of accounts
-- 1:1 with stg_accounts plus derived analytical columns:
--   - is_balance_sheet / is_income_statement: classify accounts for reporting
--   - normal_balance: 'Debit' or 'Credit' per the accounting T-rule.
--     Enables sign normalization in dashboards without replicating logic.
-- Consumed by the dashboard and the AI layer to label fact rows.

WITH source AS (
    SELECT * FROM {{ ref('stg_accounts') }}
)

SELECT
    account_id,
    account_code,
    account_name,
    account_type,
    parent_account_id,
    is_active,
    created_at,

    -- Classification flags
    CASE
        WHEN account_type IN ('Asset', 'Liability', 'Equity') THEN TRUE
        ELSE FALSE
    END AS is_balance_sheet,

    CASE
        WHEN account_type IN ('Revenue', 'Expense') THEN TRUE
        ELSE FALSE
    END AS is_income_statement,

    -- Normal balance per T-account rule
    CASE
        WHEN account_type IN ('Asset', 'Expense') THEN 'Debit'
        WHEN account_type IN ('Liability', 'Equity', 'Revenue') THEN 'Credit'
    END AS normal_balance

FROM source