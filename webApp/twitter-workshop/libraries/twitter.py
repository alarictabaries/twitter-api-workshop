# Operations with Twitter's API

import tweepy
from . import mongodb
import datetime
import pytz
from bson.objectid import ObjectId
import time


# Save tweets meeting the criteria to a CSV file
def scrape_twitter(keyword, count, lang):
    date_now = datetime.datetime.now()

    # Connect to Twitter's API
    auth = tweepy.OAuthHandler('y3fvWam4738fGFCSuVJpIhtwp', 'czDAPY4XnYe4fp4n6FMwrHSFGtF0nY15PgnmozeBAsnObHiKJr')
    auth.set_access_token('229596006-BzKTTM85v2Ca0xf7d11CPM7AKhIOnx03EsUNjgsk',
                          'FnyvhnqiKtRCroJ1iX1qaLxtrn7uEDgXONGplAxZv230V')
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Write tweets
    db = mongodb.db_connect()
    col = db["tweets"]
    _docs = []

    # Create new document every 1k tweets
    i = 0
    for tweet in tweepy.Cursor(api.search, q=keyword, lang=lang, tweet_mode='extended', result_type="recent",
                               include_entities=True).items(count):
        if i % 1000 == 0:
            _tweets = col.insert_one({"tweets": []})
            _docs.append(_tweets.inserted_id)
        col.update_one({'_id': ObjectId(_tweets.inserted_id)}, {'$push': {'tweets': tweet._json}})
        i += 1

    col = db["index"]

    # Write metadata
    col.insert_one({
        "keyword": keyword,
        "options": {
            "count": count,
            "lang": lang,
        },
        "_tweets": _docs,
        "created_at": date_now.strftime("%Y-%m-%d %H:%M")
    })

    return 1


# Read metadata from DB
def get_metadata(_id):
    db = mongodb.db_connect()
    col = db["index"]

    # Read the metadata document
    doc = col.find_one({"_id": ObjectId(_id)})

    return doc


# Get interactions
def get_interactions(tweets):

    interactions = {}
    nodes = []
    links = []

    for tweet in tweets:
        node_buffer = {"id": tweet["user"]["id"], "id_str": tweet["user"]["id_str"], "type": 1, "mentions": 0}
        unique = 0
        for node in nodes:
            if node_buffer["id"] == node["id"]:
                unique = 1
                if node["type"] == 2:
                    node["type"] = 1
        if unique == 0:
            nodes.append(node_buffer)
        # Iterate over mentions
        mentions = []
        for user in tweet['entities']['user_mentions']:
            if user and (user['id'] != tweet["user"]["id"]): # The user can't mention himself
                node_buffer = {"id": user['id'], "id_str": user['id_str'], "type": 2, "mentions": 0}
                if user['id'] not in mentions:
                    links.append({"source": tweet["user"]["id"], "target": user['id'], "value": 1})
                mentions.append(user['id'])
                unique = 0
                for node in nodes:
                    if node_buffer["id"] == node["id"]:
                        unique += 1
                if unique == 0:
                    nodes.append(node_buffer)

    for link in links:
        for node in nodes:
            if node["id"] == link["target"]:
                node["mentions"] += 1

    # Descending sort
    nodes.sort(key=lambda e: e['mentions'], reverse=True)
    nodes = nodes[:500]

    links_buffer = []
    for link in links:
        connected = 0
        for node in nodes:
            if node["id"] == link["target"]:
                connected += 1
            if node["id"] == link["source"]:
                connected += 1
        if (connected != 0) and (connected % 2 == 0):
            links_buffer.append(link)

    links = links_buffer

    interactions["nodes"] = nodes
    interactions["links"] = links

    return interactions


# Get user's details
def get_user_details(_id):
    # Connect to Twitter's API
    auth = tweepy.OAuthHandler('y3fvWam4738fGFCSuVJpIhtwp', 'czDAPY4XnYe4fp4n6FMwrHSFGtF0nY15PgnmozeBAsnObHiKJr')
    auth.set_access_token('229596006-BzKTTM85v2Ca0xf7d11CPM7AKhIOnx03EsUNjgsk',
                          'FnyvhnqiKtRCroJ1iX1qaLxtrn7uEDgXONGplAxZv230V')
    api = tweepy.API(auth, wait_on_rate_limit=True)

    user = api.get_user(_id)

    return user._json


# Define X (count) most engaged nodes in an interactions list
def get_influencers(interactions, count):
    nodes = interactions["nodes"]

    # Descending sort - No need to sort anymore since the dict is sorted in previous func
    # nodes.sort(key=lambda e: e['mentions'], reverse=True)

    # Take the X first
    influencers = nodes[:count]

    # Add user profile
    for node in influencers:
        user = get_user_details(node["id"])
        node["profile_image_url"] = user["profile_image_url"].replace("_normal", "_bigger")
        node["name"] = user["name"]
        node["screen_name"] = user["screen_name"]
        node["followers_count"] = user["followers_count"]

    return influencers


def ceil_dt(dt, delta):
    return dt + (datetime.datetime.min - dt) % delta


# Get tweets
def get_tweets(_ids):
    tweets = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["tweets"]

    for _id in _ids:

        doc = col.find_one({"_id": ObjectId(_id)})

        # Iterate over tweets
        for tweet in doc["tweets"]:
            tweets.append(tweet)

    return tweets


# Get count of tweets
def get_tweets_count(tweets):
    return len(tweets)


# Get count of users involved
def get_users_count(tweets):
    users = []

    for tweet in tweets:
        i = 0
        for user in users:
            if tweet["user"]["id"] == user:
                i += 1
        if i == 0:
            users.append(tweet["user"]["id"])

    return len(users)


# Get count of interactions
def get_interactions_count(tweets):
    interactions = 0

    for tweet in tweets:
        if tweet['entities']['user_mentions']:
            interactions += 1

    return interactions


# Get statistics per time unit
def get_stats_per_time_unit(tweets, unit):

    if unit == "m":
        time_format = "%Y-%m-%d %H:%M"
    elif unit == "h":
        time_format = "%Y-%m-%d %H:00"
    elif unit == "d":
        time_format = "%Y-%m-%d 00:00"

    distribution = []

    for tweet in tweets:
        created = 0

        created_at = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
        created_at = created_at.strftime(time_format)

        for timeframe in distribution:
            if created_at == timeframe["timeframe"]:
                created += 1

        if created is 0:
            distribution.append({"timeframe": created_at})

    for timeframe in distribution:

        tweets_buffer = []

        for tweet in tweets:
            created_at = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
            created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
            created_at = created_at.strftime(time_format)

            if created_at == timeframe["timeframe"]:
                tweets_buffer.append(tweet)

        timeframe["tweets_count"] = get_tweets_count(tweets_buffer)
        timeframe["users_count"] = get_users_count(tweets_buffer)
        timeframe["interactions_count"] = get_interactions_count(tweets_buffer)

    return distribution
