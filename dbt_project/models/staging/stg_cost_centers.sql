-- Staging model for the cost centers dimension
-- Casts types, renames columns where appropriate, and exposes
-- the table for downstream intermediate and marts models.

with source as (

    select * from {{ source('raw', 'raw_cost_centers') }}

),

renamed as (

    select
        cost_center_id,
        code,
        name,
        department,
        manager_name,
        is_active,
        cast(created_at as timestamp) as created_at
    from source

)

select * from renamed