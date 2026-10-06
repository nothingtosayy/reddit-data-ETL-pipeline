-- Future records should not exist in the silver_users table
-- If it returns any records, it means that the incremental model is not working as expected

select *
from {{ref('silver_users')}}
where record_synced_at > current_timestamp()