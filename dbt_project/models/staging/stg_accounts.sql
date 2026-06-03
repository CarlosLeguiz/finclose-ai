-- Staging model for the accounts dimension
-- Casts types, renames columns where appropriate, and exposes
-- the table for downstream intermediate and marts models.

with source as (

    select * from {{ source('raw', 'raw_accounts') }}

),

renamed as (

    select
        account_id,
        account_code,
        account_name,
        account_type,
        parent_account_id,
        is_active,
        cast(created_at as timestamp) as created_at

    from source

)

select * from renamed