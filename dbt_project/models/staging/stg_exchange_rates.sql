-- Staging model for the exchange rates dimension
-- Monthly conversion rates between currencies (USD/ARS, EUR/ARS) from BCRA.

with source as (

    select * from {{ source('raw', 'raw_exchange_rates') }}

),

renamed as (

    select
        rate_id,
        from_currency,
        to_currency,
        cast(rate_date as date) as rate_date,
        rate,
        source as rate_source,
        cast(created_at as timestamp) as created_at
    from source

)

select * from renamed