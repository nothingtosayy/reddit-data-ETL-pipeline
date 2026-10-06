
{{config(
    materialized='incremental',
    unique_key='record_hash',
    file_format='delta',
    partition_by='record_synced_at',
    location_root='s3://reddit-data-2009/gold_dbt',
)}}

SELECT * FROM {{ ref('silver_users') }}
WHERE 1=1
{% if is_incremental() %}
    AND record_synced_at > (select max(record_synced_at) from {{ this }})
{% endif %}

ORDER BY id;

