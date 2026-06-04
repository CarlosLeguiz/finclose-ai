-- Staging model for budget allocations
-- 6768 budgets for Revenue/Expense accounts across cost centers and periods.

with source as (

    select * from {{ source('raw', 'raw_budgets') }}

),

renamed as (

    select
        budget_id,
        account_id,
        cost_center_id,
        period_id,
        cast(budgeted_amount as decimal(18, 2)) as budgeted_amount,
        currency,
        budget_version,
        is_active,
        cast(created_at as timestamp) as created_at
    from source

)

select * from renamed