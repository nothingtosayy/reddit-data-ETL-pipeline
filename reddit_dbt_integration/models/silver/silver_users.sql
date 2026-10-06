
{{config(
    materialized='incremental',
    unique_key='record_hash',
    file_format='delta',
    partition_by='record_synced_at',
    location_root='s3://reddit-data-2009/silver_dbt',
)}}

WITH source_combined_data AS(
    SELECT MD5(CONCAT( 
        SPLIT(record_id, ':')[1]::STRING,
        username, 
        profile_url,
        subreddit,
        posts_in_subreddit,
        comments_in_subreddit,
        collection_scope,
        first_seen_post_title,
        source_listing_url
        )) AS record_hash, 
        id, 
        SPLIT(record_id, ':')[1]::STRING as recordId,
        username, 
        profile_url,
        subreddit,
        posts_in_subreddit,
        comments_in_subreddit,
        collection_scope,
        first_seen_post_title,
        source_listing_url,
        _fivetran_synced as record_synced_at
    FROM {{ source('reddit-source', 'users') }}
)

SELECT id, 
        recordId,
        username, 
        profile_url,
        subreddit,
        posts_in_subreddit,
        comments_in_subreddit,
        collection_scope,
        first_seen_post_title,
        source_listing_url,
        record_synced_at,
        record_hash
         
FROM source_combined_data
WHERE 1 = 1

{% if is_incremental() %}
    AND record_synced_at > (select max(record_synced_at) from {{ this }})
{% endif %}

ORDER BY id;