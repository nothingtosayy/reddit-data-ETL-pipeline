-- User's username should be part of profile_url in the silver_users table
-- If not, the data is not correctly coming from the source. 
-- and we have to intimate the source team to fix the issue. or we have to include this as part of the transformation to clean the profile url


select *
from {{ref('silver_users')}}
where SPLIT(profile_url, '/')[4] <> username