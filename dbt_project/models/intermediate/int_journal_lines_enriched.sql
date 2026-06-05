-- Intermediate model: journal lines enriched with dimensional context
-- Joins stg_journal_lines with accounts, cost centers, entries, and periods
-- to produce a fully contextualized view of every debit/credit movement.
-- No business filters applied — downstream marts decide their own cuts.

with journal_lines as (

    select * from {{ ref('stg_journal_lines') }}

),

accounts as (

    select * from {{ ref('stg_accounts') }}

),

cost_centers as (

    select * from {{ ref('stg_cost_centers') }}

),

journal_entries as (

    select * from {{ ref('stg_journal_entries') }}

),

periods as (

    select * from {{ ref('stg_periods') }}

),

enriched as (

    select
        -- Line identification
        jl.je_line_id,
        jl.je_id,
        jl.line_number,

        -- Account context
        jl.account_id,
        a.account_code,
        a.account_name,
        a.account_type,

        -- Cost center context
        jl.cost_center_id,
        cc.code         as cost_center_code,
        cc.name         as cost_center_name,
        cc.department,

        -- Period context (via journal entry)
        je.period_id,
        p.year          as period_year,
        p.month         as period_month,
        p.quarter       as period_quarter,
        p.is_closed     as period_is_closed,

        -- Entry context
        je.entry_date,
        je.description  as entry_description,
        je.source_system,
        je.status       as entry_status,
        je.created_by,

        -- Amounts and currency
        jl.debit_amount,
        jl.credit_amount,
        jl.currency,

        -- Line description
        jl.description  as line_description

    from journal_lines  jl
    left join accounts          a   on jl.account_id      = a.account_id
    left join cost_centers      cc  on jl.cost_center_id  = cc.cost_center_id
    left join journal_entries   je  on jl.je_id           = je.je_id
    left join periods           p   on je.period_id       = p.period_id

)

select * from enriched