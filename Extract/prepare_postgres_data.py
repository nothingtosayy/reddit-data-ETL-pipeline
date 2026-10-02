import psycopg2
import boto3
import dotenv
import os
import json

dotenv.load_dotenv()

password = "postgres123"

conn = None

db_name = "reddit_users"  # Replace with your desired database name

reddit_users_list = list()

# try:
#     conn = psycopg2.connect(
#         host="localhost",
#         port=5432,
#         database="postgres",
#         user="postgres",
#         password=password,
#         sslmode="require"
#     )
#     cur = conn.cursor()
#     print("PostgreSQL connection successful!")

#     # Important: CREATE DATABASE cannot run inside a transaction
#     conn.autocommit = True

#     try:
#         cur.execute(f"CREATE DATABASE {db_name};")
#         print("Database created successfully!")
#     except psycopg2.errors.DuplicateDatabase:
#         print("Database already exists.")
#     except Exception as e:
#         print(f"Error creating database: {e}")
#         raise e

#     conn.close()
# except Exception as e:
#     print(f"Database error: {e}")
#     raise
# finally:
#     if conn:
#         conn.close()

def insert_data(cur, table_name):
    # Create a boto3 client for S3
    # Let's use Amazon S3
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    paginator = s3.get_paginator("list_objects_v2")

    prefix = 'users/'

    for page in paginator.paginate(
        Bucket=BUCKET_NAME,
        Prefix=prefix
    ):
        for obj in page.get("Contents", []):

            s3_key = obj["Key"]

            if not s3_key.endswith(".json"):
                continue

            response = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=s3_key
            )

            data = json.loads(
                response["Body"].read().decode("utf-8")
            )

            print(f"Processing: {s3_key}")
            reddit_users_list.extend(data)

    print(f"Total user records fetched from S3: {len(reddit_users_list)}")

    inserted_records_count = 0
    for user_record in reddit_users_list:
        if user_record.get("recordType") != "subreddit_user":
            continue  # Skip records that are not subreddit users

        insert_sql = f"""
            INSERT INTO {table_name} (
                username, profile_url, subreddit, collection_scope,
                posts_in_subreddit, comments_in_subreddit,
                first_seen_post_title, source_listing_url, record_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """

        try:
            cur.execute(insert_sql, (
                user_record.get("username"),
                user_record.get("profileUrl"),
                user_record.get("subreddit"),
                user_record.get("collectionScope"),
                int(user_record.get("postsInSubreddit")),
                int(user_record.get("commentsInSubreddit")),
                user_record.get("firstSeenPostTitle"),
                user_record.get("sourceListingUrl"),
                user_record.get("recordId")
            ))

            inserted_records_count += 1
            print("User Record Inserted Successfully:", user_record.get("username"))
        except Exception as e:
            print(f"Error inserting record for user {user_record.get('username')}: {e}")
            continue  # Continue with the next record even if there's an error

    print(f"Total user records inserted into the database: {inserted_records_count}")

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database=db_name,
        user="postgres",
        password=password,
        sslmode="require"
    )
    cur = conn.cursor()
    print("PostgreSQL connection successful!")

    # Important: CREATE DATABASE cannot run inside a transaction
    # conn.autocommit = True

    print(f"Connected to the database {db_name} successfully!")

    create_sql = """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    profile_url VARCHAR(255) NOT NULL,
                    subreddit VARCHAR(255) NOT NULL,
                    collection_scope VARCHAR(255) NOT NULL,
                    posts_in_subreddit INTEGER NOT NULL,
                    comments_in_subreddit INTEGER NOT NULL,
                    first_seen_post_title VARCHAR(255) NOT NULL,
                    source_listing_url VARCHAR(255) NOT NULL,
                    record_id VARCHAR(255) NOT NULL
                );"""

    cur.execute(create_sql)
    print(f"Table 'users' created or already exists in database {db_name}.")


    # Insert data into the table
    insert_data(cur, 'users')

#     cur.execute("""SELECT table_schema, table_name
# FROM information_schema.tables
# ORDER BY table_schema, table_name;""")
#     results = cur.fetchall()
#     print("Retrieved records from the database:")
#     for row in results:
#         print(row)
    # cur.execute("""
    # SELECT schemaname, tablename
    # FROM pg_catalog.pg_tables
    # WHERE tablename = 'users';
    # """)

    # print(cur.fetchall())

    conn.commit()

    conn.close()
except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
        conn.close()