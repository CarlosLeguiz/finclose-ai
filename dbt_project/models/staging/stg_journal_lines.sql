-- Staging model for journal entry lines
-- 12591 lines following double-entry bookkeeping (debit total = credit total per entry).

with source as (

    select * from {{ source('raw', 'raw_journal_lines') }}

),

renamed as (

    select
        je_line_id,
        je_id,
        line_number,
        account_id,
        cost_center_id,
        cast(debit_amount as decimal(18, 2)) as debit_amount,
        cast(credit_amount as decimal(18, 2)) as credit_amount,
        currency,
        description,
        cast(created_at as timestamp) as created_at
    from source

)

select * from renamed