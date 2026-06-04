-- Staging model for the accounting periods dimension
-- Casts types and exposes 36 monthly periods (2024-2026) for downstream models.

with source as (

    select * from {{ source('raw', 'raw_periods') }}

),

renamed as (

    select
        period_id,
        year,
        month,
        period_name,
        quarter,
        cast(start_date as date) as start_date,
        cast(end_date as date) as end_date,
        is_closed,
        cast(closed_at as timestamp) as closed_at
    from source

)

select * from renamed