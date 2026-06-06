-- Mart dimension: cost centers with department metadata
-- 1:1 with stg_cost_centers plus derived columns:
--   - has_manager: flag for cost centers with an assigned responsible person
--   - department_group: high-level grouping for executive reporting
-- Consumed by the dashboard and AI layer to label and group fact rows.

WITH source AS (
    SELECT * FROM {{ ref('stg_cost_centers') }}
)

SELECT
    cost_center_id,
    code,
    name,
    department,
    manager_name,
    is_active,
    created_at,

    -- Derived flags
    CASE
        WHEN manager_name IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS has_manager,

    -- High-level department grouping for executive reporting
    CASE
        WHEN department IN ('Operations', 'Manufacturing', 'Logistics') THEN 'Operations'
        WHEN department IN ('Sales', 'Marketing') THEN 'Commercial'
        WHEN department IN ('Finance', 'HR', 'IT', 'Legal', 'G&A') THEN 'Support'
        ELSE 'Other'
    END AS department_group

FROM source