-- Singular test: cost_center_id assignment rules per account_type
-- Business rule:
--   - Expense and Revenue lines MUST have a cost_center_id (cost responsibility)
--   - Asset, Liability, and Equity lines MUST have cost_center_id NULL
--     (balance sheet items don't belong to a department)
-- Returns violating rows. 0 rows = test passes.

WITH lines_with_type AS (
    SELECT
        jl.je_line_id,
        jl.cost_center_id,
        a.account_type
    FROM {{ ref('stg_journal_lines') }} jl
    LEFT JOIN {{ ref('stg_accounts') }} a ON jl.account_id = a.account_id
)

SELECT *
FROM lines_with_type
WHERE
    -- Expense/Revenue without cost center (violation)
    (account_type IN ('Expense', 'Revenue') AND cost_center_id IS NULL)
    OR
    -- Asset/Liability/Equity with cost center (violation)
    (account_type IN ('Asset', 'Liability', 'Equity') AND cost_center_id IS NOT NULL)