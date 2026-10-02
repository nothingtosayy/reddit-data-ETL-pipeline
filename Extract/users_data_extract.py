from apify_client import ApifyClient
import dotenv
import os
import json
from datetime import datetime
import pytz
import boto3


local_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")  # Get the current local time with timezone information

dotenv.load_dotenv()  # Load environment variables from .env file

# Initialize the ApifyClient with your API token
apify_token = os.getenv("APIFY_TOKEN")
apify_actor = os.getenv("APIFY_ACTOR")  # Get the Apify actor name from environment variables

client = ApifyClient(apify_token)

current_timestamp = datetime.now().strftime("%d%m%Y%H%M")

# "https://www.reddit.com/r/dataengineering" 
# https://www.reddit.com/r/ThirtiesIndia

# Prepare the Actor input
subreddits = ["dataengineering", 
                "dataengineersindia",
                "dataengineeringjobs"]

all_items_list = []
for subreddit in subreddits:
    run_input = {
    "subreddit": subreddit,
    "sortBy": "new",
    "topTime": "week",
    "maxPosts": 20,
    "includeCommentAuthors": False,
    "fetchProfileDetails": True,
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"]
    }
    }

    # Run the Actor and wait for it to finish
    run = client.actor("w3crawler/reddit-subreddit-users-scraper").call(run_input=run_input)

    # Fetch and print Actor results from the run's dataset (if there are any)
    all_items = list(client.dataset(run.default_dataset_id).iterate_items())
    all_items_list.extend(all_items)  # Append the items to the main list


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

# Print out bucket names
# response = s3.list_buckets()
# for bucket in response['Buckets']:
#     print(bucket['Name'])


try:
    # Upload the JSON data to S3
    curr_timestamp = datetime.now().strftime("%d%m%Y%H%M")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"users/reddit_users_{curr_timestamp}.json",
        Body=json.dumps(all_items_list, indent=4),
        ContentType='application/json'
    )
    print(f"Data uploaded to S3 bucket '{BUCKET_NAME}' as 'users/reddit_users_{curr_timestamp}.json'")
except Exception as e:
    print(f"Error uploading data to S3: {e}")
