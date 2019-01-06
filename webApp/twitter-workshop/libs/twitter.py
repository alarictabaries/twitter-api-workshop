# Operations with Twitter's API and Twitter's data

import tweepy
from . import mongodb
from . import misc
from datetime import datetime, timedelta
import pytz
from bson.objectid import ObjectId


# Save tweets meeting the criteria to MongoDB
def create_query(keyword, count, lang, _user):

    date_now = datetime.utcnow()

    # Connect to Twitter's API
    auth = tweepy.OAuthHandler('y3fvWam4738fGFCSuVJpIhtwp', 'czDAPY4XnYe4fp4n6FMwrHSFGtF0nY15PgnmozeBAsnObHiKJr')
    auth.set_access_token('229596006-BzKTTM85v2Ca0xf7d11CPM7AKhIOnx03EsUNjgsk',
                          'FnyvhnqiKtRCroJ1iX1qaLxtrn7uEDgXONGplAxZv230V')
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Write tweets
    db = mongodb.db_connect()

    col = db["app_queries"]

    # Write metadata
    _query = col.insert_one({
        "_user": _user,
        "keyword": keyword,
        "lang": lang,
        "count": 0,
        "created": date_now.strftime("%Y-%m-%d %H:%M"),
        "updated": None
    })

    col = db["app_tweets"]

    if count > 0:

        last_update = None
        real_count = 0

        for tweet in tweepy.Cursor(api.search, q=keyword, lang=lang, tweet_mode='extended', result_type="recent",
                                   include_entities=True).items(count):

            if last_update is None:
                created_at = datetime.strptime(tweet._json["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
                created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
                last_update = created_at
            real_count += 1
            tweet._json["_query"] = _query.inserted_id
            col.insert_one(tweet._json)

        col = db["app_queries"]

        col.update_one({'_id': ObjectId(_query.inserted_id)},
                       {"$set": {
                            "count" : real_count,
                            "updated": last_update
                       }})

    return 1


# Scrape tweets created after specific date
def update_query(_query):

    metadata = get_metadata(_query)

    # Connect to Twitter's API
    auth = tweepy.OAuthHandler('y3fvWam4738fGFCSuVJpIhtwp', 'czDAPY4XnYe4fp4n6FMwrHSFGtF0nY15PgnmozeBAsnObHiKJr')
    auth.set_access_token('229596006-BzKTTM85v2Ca0xf7d11CPM7AKhIOnx03EsUNjgsk',
                          'FnyvhnqiKtRCroJ1iX1qaLxtrn7uEDgXONGplAxZv230V')
    api = tweepy.API(auth, wait_on_rate_limit=True)

    db = mongodb.db_connect()
    col = db["app_tweets"]

    real_count = metadata["count"]
    last_update = None

    if metadata["updated"] is None:
        updated = metadata["created"]
    else:
        updated = metadata["updated"]

    for tweet in tweepy.Cursor(api.search, q=metadata["keyword"], lang=metadata["lang"], tweet_mode='extended', result_type="recent", include_entities=True).items():

        created_at = datetime.strptime(tweet._json["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

        if created_at > updated:

            if last_update is None:
                last_update = created_at

            real_count += 1
            tweet._json["_query"] = metadata["_id"]
            col.insert_one(tweet._json)

        else:
            break

    col = db["app_queries"]

    if last_update is None:
        last_update = metadata["updated"]

    col.update_one({'_id': ObjectId(metadata["_id"])},
                   {"$set": {
                       "count": real_count,
                       "updated": last_update
                   }})

    return real_count - metadata["count"]


# Read metadata from DB
def get_metadata(_id):
    db = mongodb.db_connect()
    col = db["app_queries"]

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

    nodes_buffer = []
    for node in nodes:
        lonely = 0
        for link in links:
            if node["id"] == link["source"] or node["id"] == link["target"]:
                lonely += 1
        if lonely > 0:
            nodes_buffer.append(node)

    nodes = nodes_buffer

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


# Get influencers
def get_influencers(interactions, count):
    return 0


# Get impacting tweets
def get_impacting_tweets(tweets, count):

    impacting_tweets = []

    for tweet in tweets:

        redundant = 0

        try:
            tweet["retweeted_status"]
        except KeyError:
            tweet["retweeted_status"] = None
        if tweet["retweeted_status"] is not None:
            id = tweet["retweeted_status"]["id"]
            full_text = tweet["retweeted_status"]["full_text"]
        else:
            id = tweet["id"]
            full_text = tweet["full_text"]

        for impacting_tweet in impacting_tweets:
            if impacting_tweet[0] == id:
                redundant += 1
                impacting_tweet[2] += 1

        if redundant == 0:
            impacting_tweets.append([id, full_text, 0])

    impacting_tweets.sort(key=lambda x: x[2], reverse=True)

    return impacting_tweets[:count]


# Get tweets
def get_tweets(_id):
    tweets = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["app_tweets"]

    docs = col.find({"_query": ObjectId(_id)})

    for doc in docs:
        tweets.append(doc)

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


# Get tweets in a timeframe
# Boundaries date format : %Y-%m-%d %H:%M
def get_tweets_by_timeframe(tweets, start_date, end_date):

    tweets_buffer = []
    for tweet in tweets:
        created_at = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
        created_at = created_at.strftime("%Y-%m-%d %H:%M")

        if start_date <= created_at < end_date:
            tweets_buffer.append(tweet)

    return tweets_buffer


# Get statistics per time unit
def get_stats_per_time_unit(tweets, unit, start_date, end_date):

    distribution = []

    if unit == "m":
        time_format = "%Y-%m-%d %H:%M"
    elif unit == "h":
        time_format = "%Y-%m-%d %H:00"
        for timeframe in misc.perdelta(datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d"),timedelta(hours=1)):
            distribution.append({"timeframe": timeframe.strftime(time_format)})
    elif unit == "d":
        time_format = "%Y-%m-%d 00:00"
        for timeframe in misc.perdelta(datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d"),timedelta(days=1)):
            distribution.append({"timeframe": timeframe.strftime(time_format)})

    distribution.sort(key=lambda x: x['timeframe'])

    for timeframe in distribution:

        tweets_buffer = []

        for tweet in tweets:
            created_at = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
            created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
            created_at = created_at.strftime(time_format)

            if created_at == timeframe["timeframe"]:
                tweets_buffer.append(tweet)

        if tweets_buffer:
            timeframe["tweets_count"] = get_tweets_count(tweets_buffer)
            timeframe["users_count"] = get_users_count(tweets_buffer)
            timeframe["interactions_count"] = get_interactions_count(tweets_buffer)
        else:
            timeframe["tweets_count"] = 0
            timeframe["users_count"] = 0
            timeframe["interactions_count"] = 0

    return distribution
