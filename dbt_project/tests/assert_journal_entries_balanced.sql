-- Singular test: every journal entry must balance (debit = credit)
-- Core accounting invariant: in double-entry bookkeeping, the sum of debits
-- must equal the sum of credits within each journal entry.
-- This test returns rows that VIOLATE the rule. If 0 rows, test passes.
-- A failure here indicates a fundamental data integrity problem.

SELECT
    je_id,
    SUM(debit_amount) AS total_debit,
    SUM(credit_amount) AS total_credit,
    SUM(debit_amount) - SUM(credit_amount) AS imbalance
FROM {{ ref('stg_journal_lines') }}
GROUP BY je_id
HAVING ABS(SUM(debit_amount) - SUM(credit_amount)) > 0.01