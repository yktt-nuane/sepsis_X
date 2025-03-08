import json
import os
import boto3
import tweepy
from datetime import datetime, timedelta
import pytz

def get_twitter_credentials():
    """Retrieve Twitter API credentials from AWS Secrets Manager."""
    secret_name = "twitter-api-keys"
    region_name = "ap-northeast-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        raise e
    else:
        # Parse the secret JSON
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            return {
                'api_key': secret.get('api_key'),
                'api_key_secret': secret.get('api_key_secret'),
                'access_token': secret.get('access_token'),
                'access_token_secret': secret.get('access_token_secret'),
                'bearer_token': secret.get('bearer_token')
            }

    return None

def post_to_twitter(api_key, api_key_secret, access_token, access_token_secret, bearer_token):
    """Post to Twitter using the Tweepy library."""
    # Get the current date in Japan timezone
    japan_timezone = pytz.timezone('Asia/Tokyo')
    today = datetime.now(japan_timezone).strftime('%Y-%m-%d')

    # Create message
    message = f"""✅本日の敗血症
https://www.sepsis-search.com/articles?date={today}"""

    # Set up Tweepy Client using Twitter API v2
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Post tweet
    try:
        response = client.create_tweet(text=message)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Tweet posted successfully!',
                'tweet_id': response.data['id']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error posting tweet: {str(e)}'
            })
        }

def lambda_handler(event, context):
    """Lambda function handler to post daily sepsis update to Twitter."""
    try:
        # Get Twitter credentials from Secrets Manager
        twitter_creds = get_twitter_credentials()

        if not twitter_creds:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to retrieve Twitter credentials')
            }

        # Post to Twitter
        return post_to_twitter(
            twitter_creds['api_key'],
            twitter_creds['api_key_secret'],
            twitter_creds['access_token'],
            twitter_creds['access_token_secret'],
            twitter_creds['bearer_token']
        )

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error in lambda_handler: {str(e)}'
            })
        }
