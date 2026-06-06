-- Mart dimension: enriched accounting periods (calendar dimension)
-- 1:1 with stg_periods plus derived columns for time-based analysis:
--   - period_label: human-readable label for charts (e.g. "Jan 2026")
--   - fiscal_year_label: formatted year for grouping
--   - quarter_label: formatted quarter (e.g. "2026-Q1")
--   - is_current_period / is_prior_year_period: flags for relative-time queries
--   - days_in_period: useful for daily-average calculations
-- Consumed by dashboard for time-series visualizations and period comparisons.

WITH source AS (
    SELECT * FROM {{ ref('stg_periods') }}
)

SELECT
    period_id,
    year,
    month,
    quarter,
    period_name,
    start_date,
    end_date,
    is_closed,
    closed_at,

    -- Display labels for charts
    period_name AS period_label,
    CAST(year AS VARCHAR) AS fiscal_year_label,
    CAST(year AS VARCHAR) || '-Q' || CAST(quarter AS VARCHAR) AS quarter_label,

    -- Days in the period (useful for daily averages)
    DATE_DIFF('day', start_date, end_date) + 1 AS days_in_period,

    -- Relative-time flags (computed against current date)
    CASE
        WHEN year = EXTRACT(YEAR FROM CURRENT_DATE)
         AND month = EXTRACT(MONTH FROM CURRENT_DATE)
        THEN TRUE ELSE FALSE
    END AS is_current_period,

    CASE
        WHEN year = EXTRACT(YEAR FROM CURRENT_DATE) - 1
         AND month = EXTRACT(MONTH FROM CURRENT_DATE)
        THEN TRUE ELSE FALSE
    END AS is_prior_year_same_period

FROM source