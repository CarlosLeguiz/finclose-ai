-- Intermediate model: actuals aggregated by (account, cost_center, period)
-- Sums debit/credit amounts per intersection, filtering to Posted entries only.
-- Forms the base for any actual-vs-budget variance analysis in marts.

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