-- Singular test: int_actuals_full preserves Posted journal line totals
-- The aggregation in int_actuals_full must NOT lose money: the sum of debits
-- and credits at aggregate level must equal the sum at the raw line level
-- (Posted entries only).
-- A discrepancy here indicates a bug in the aggregation logic.

WITH staging_totals AS (
    SELECT
        SUM(jl.debit_amount) AS staging_debit,
        SUM(jl.credit_amount) AS staging_credit
    FROM {{ ref('stg_journal_lines') }} jl
    INNER JOIN {{ ref('stg_journal_entries') }} je ON jl.je_id = je.je_id
    WHERE je.status = 'Posted'
),

intermediate_totals AS (
    SELECT
        SUM(total_debit) AS int_debit,
        SUM(total_credit) AS int_credit
    FROM {{ ref('int_actuals_full') }}
)

SELECT
    s.staging_debit,
    i.int_debit,
    s.staging_credit,
    i.int_credit,
    ABS(s.staging_debit - i.int_debit) AS debit_diff,
    ABS(s.staging_credit - i.int_credit) AS credit_diff
FROM staging_totals s
CROSS JOIN intermediate_totals i
WHERE
    ABS(s.staging_debit - i.int_debit) > 0.01
    OR ABS(s.staging_credit - i.int_credit) > 0.01