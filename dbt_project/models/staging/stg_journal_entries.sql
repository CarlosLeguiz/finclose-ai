-- Staging model for journal entry headers
-- 3600 entries across 36 months, with status and source_system distributions.

with source as (

    select * from {{ source('raw', 'raw_journal_entries') }}

),

renamed as (

    select
        je_id,
        period_id,
        cast(entry_date as date) as entry_date,
        description,
        source_system,
        created_by,
        status,
        cast(created_at as timestamp) as created_at,
        cast(posted_at as timestamp) as posted_at
    from source

)

select * from renamed