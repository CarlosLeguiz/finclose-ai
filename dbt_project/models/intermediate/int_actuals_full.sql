-- Intermediate model: actuals aggregated by (account, cost_center, period)
-- Sums debit/credit amounts per intersection, filtering to Posted entries only.
-- Forms the base for any actual-vs-budget variance analysis in marts.
--
-- Two amount representations are exposed:
--   - net_amount: raw accounting convention (debit - credit).
--                 Positive for Asset/Expense, negative for Liability/Equity/Revenue.
--                 Use this for accounting-native audits.
--   - signed_amount: sign-normalized by account_type so positive always means
--                    "increase" for that account. Use this for budget vs actual
--                    comparison and any business-facing analysis.
with journal_lines_enriched as (
    select * from {{ ref('int_journal_lines_enriched') }}
    where entry_status = 'Posted'
),

aggregated as (
    select
        -- Grouping keys
        account_id,
        cost_center_id,
        period_id,
        -- Account context (carried for downstream convenience)
        account_code,
        account_name,
        account_type,
        -- Cost center context (NULL allowed for Asset/Liability/Equity)
        cost_center_name,
        department,
        -- Period context
        period_year,
        period_month,
        period_quarter,
        -- Aggregated amounts
        sum(debit_amount)                        as total_debit,
        sum(credit_amount)                       as total_credit,
        sum(debit_amount) - sum(credit_amount)   as net_amount,
        -- Sign-normalized: positive always means "increase" for the account type.
        -- Asset and Expense increase with debit, so signed_amount = debit - credit.
        -- Liability, Equity and Revenue increase with credit, so flipped.
        case
            when account_type in ('Asset', 'Expense')
                then sum(debit_amount) - sum(credit_amount)
            when account_type in ('Liability', 'Equity', 'Revenue')
                then sum(credit_amount) - sum(debit_amount)
        end                                      as signed_amount,
        -- Row count for traceability
        count(*)                                 as line_count
    from journal_lines_enriched
    group by
        account_id,
        cost_center_id,
        period_id,
        account_code,
        account_name,
        account_type,
        cost_center_name,
        department,
        period_year,
        period_month,
        period_quarter
)

select * from aggregated