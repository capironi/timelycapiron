import os
import random
import requests
import tweepy


# Pick a random image/video from the 'assets' folder
def get_random_media():
    path = 'assets'
    if not os.path.exists(path):
        raise FileNotFoundError(f"The directory '{path}' does not exist.")
    
    # Filter for media files only
    media_files = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif'))]
    if not media_files:
        raise FileNotFoundError(f"No media files found in the directory '{path}'.")
    
    media = random.choice(media_files)
    return os.path.join(path, media)


# Authorize Twitter with v1.1 API
def auth_v1(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


# Authorize Twitter with v2 API
def auth_v2(consumer_key, consumer_secret, access_token, access_token_secret):
    return tweepy.Client(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret,
        return_type=requests.Response,
    )


# Read captions from a .txt file and pick a random one
def get_random_caption(file_path='captions.txt'):
    try:
        with open(file_path, 'r') as file:
            captions = file.readlines()
        # Choose a random caption and strip any extra whitespace
        return random.choice(captions).strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    except Exception as e:
        raise Exception(f"Error reading captions from file: {e}")


# Tweet picked image/video with a caption
def tweet(media, caption="") -> tweepy.Response:
    try:
        # Get Twitter API credentials from environment variables
        consumer_key = os.environ['CONSUMER_KEY']
        consumer_secret = os.environ['CONSUMER_SECRET']
        access_token = os.environ['ACCESS_TOKEN']
        access_token_secret = os.environ['ACCESS_TOKEN_SECRET']
    except KeyError as e:
        raise EnvironmentError(f"Missing environment variable: {e.args[0]}")

    # Authenticate with Twitter APIs
    api_v1 = auth_v1(consumer_key, consumer_secret, access_token, access_token_secret)
    client_v2 = auth_v2(consumer_key, consumer_secret, access_token, access_token_secret)

    try:
        # Upload media and get media ID
        media_id = api_v1.media_upload(media).media_id
    except tweepy.TweepError as e:
        raise Exception(f"Media upload failed: {e}")

    try:
        # Post tweet with media and optional caption
        response = client_v2.create_tweet(media_ids=[media_id], text=caption)
        return response
    except tweepy.TweepError as e:
        raise Exception(f"Tweet creation failed: {e}")


def main():
    try:
        media = get_random_media()  # Get random media
        caption = get_random_caption('captions.txt')  # Get a random caption from the file
        response = tweet(media, caption)  # Tweet the media with caption
        print(f"Tweet successfully posted: {response.data}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
