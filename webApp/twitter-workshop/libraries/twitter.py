# Operations with Twitter's API

import tweepy
from . import mongodb
import datetime
import pytz
from bson.objectid import ObjectId
import json


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


# Get tweets from DB
def get_tweets(_ids):
    tweets_data = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["tweets"]

    for _id in _ids:

        doc = col.find_one({"_id": ObjectId(_id)})

        # Iterate over tweets
        for tweet in doc["tweets"]:
            short_text = (tweet["full_text"][:125] + '..') if len(tweet["full_text"]) > 125 else tweet["full_text"]
            datetime_obj = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
            datetime_obj = datetime_obj.replace(tzinfo=pytz.timezone('UTC'))
            datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
            tweets_data.append(
                [tweet["full_text"], short_text, tweet["id_str"], tweet["user"]["screen_name"], tweet["user"]["id_str"],
                 datetime_obj])

    return tweets_data


# Get interactions
def get_interactions(_ids, **options):
    # If options are set
    start_date = options.get('start_date', None)
    end_date = options.get('end_date', None)
    threshold = options.get('threshold', None)

    interacts = {}
    nodes = []
    links = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["tweets"]

    for _id in _ids:

        doc = col.find_one({"_id": ObjectId(_id)})

        # Iterate over tweets
        for tweet in doc["tweets"]:
            created_at = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
            created_at = created_at.replace(tzinfo=pytz.timezone('UTC'))
            created_at = created_at.strftime("%Y-%m-%d %H:%M")
            tmp_node = {"id": tweet["user"]["id"], "id_str": tweet["user"]["id_str"],
                        "screen_name": tweet["user"]["screen_name"], "type": 1, "mentions": 0}
            # If date is set
            if start_date:
                # If the tweet is in the specified time frame
                if (datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M") >= datetime.datetime.strptime(start_date,
                                                                                                           "%Y-%m-%d %H:%M")) and (
                        datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M") <= datetime.datetime.strptime(
                    end_date, "%Y-%m-%d %H:%M")):
                    nodes.append(tmp_node)
            else:
                nodes.append(tmp_node)

            # Iterate over mentions
            for user in tweet['entities']['user_mentions']:
                if user and (user['id'] != tweet["user"]["id"]):  # The user can't mention himself
                    tmp_node = {"id": user['id'], "id_str": user['id_str'], "screen_name": user["screen_name"],
                                "type": 2,
                                "mentions": 0}
                    tmp_link = {"source": tweet["user"]["id"], "target": user['id'], "value": 1}
                    # If date is set
                    if start_date:
                        # If the tweet is in the specified time frame
                        if (datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M") >= datetime.datetime.strptime(
                                start_date, "%Y-%m-%d %H:%M")) and (
                                datetime.datetime.strptime(created_at,
                                                           "%Y-%m-%d %H:%M") <= datetime.datetime.strptime(
                            end_date, "%Y-%m-%d %H:%M")):
                            nodes.append(tmp_node)
                            links.append(tmp_link)
                    else:
                        nodes.append(tmp_node)
                        links.append(tmp_link)

    # Create unique nodes array
    # and determine active et inactive ones
    unique_nodes = []
    for node in nodes:
        duplicated = 0
        active = 0
        for unique_node in unique_nodes:
            if node["id"] == unique_node["id"]:
                duplicated += 1
            if (node["id"] == unique_node["id"]) and (node["type"] == 1):
                active += 1
        # Append if node read for the first time
        if duplicated == 0:
            tmp_node = {"id": node["id"], "id_str": node["id_str"], "screen_name": node["screen_name"],
                        "type": node["type"],
                        "mentions": node["mentions"]}
            unique_nodes.append(tmp_node)
        # Set the type if the node is at least one time active
        for unique_node in unique_nodes:
            if active > 0:
                if unique_node["id"] == node["id"]:
                    unique_node["type"] = 1

    # Unique links ? what if a same user tweets 5 times "@mention wtf", should we keep it? For the moment, no

    # Create unique links array
    unique_links = []
    for link in links:
        duplicated = 0
        tmp_link = {"source": link["source"], "target": link["target"], "value": link["value"]}
        for unique_link in unique_links:
            if (link["source"] == unique_link["source"]) and (link["target"] == unique_link["target"]):
                duplicated += 1
        if duplicated == 0:
            unique_links.append(tmp_link)

    nodes = unique_nodes
    links = unique_links

    # Calculate mentions frequency for nodes
    for link in unique_links:
        for node in nodes:
            if node["id"] == link["target"]:
                node["mentions"] += 1

    engaged_nodes = []

    # Remove isolated nodes
    for node in nodes:
        connected = 0
        for link in links:
            if node["id"] == link["source"] or node["id"] == link["target"]:
                connected += 1
        if connected > 0:
            engaged_nodes.append(node)

    nodes = engaged_nodes

    # If simplified is set
    if threshold is None or threshold is 0:
        interacts["nodes"] = nodes
        interacts["links"] = links

        return interacts

    engaged_nodes = []
    engaged_links = []

    # Remove small nodes (with freq < threshold
    for node in nodes:
        connected = 0
        for link in links:
            if (node["id"] == link["target"]) and (node["mentions"] >= threshold):
                connected += 1
        if connected > 0:
            engaged_nodes.append(node)

    nodes = engaged_nodes

    for link in links:
        connected = 0
        for node in nodes:
            if node["id"] == link["target"]:
                connected += 1
            if node["id"] == link["source"]:
                connected += 1
        if (connected != 0) and (connected % 2 == 0):
            engaged_links.append(link)

    links = engaged_links

    # Remove single nodes (better JS side to display or not?)
    engaged_nodes = []
    for node in nodes:
        connected = 0
        for link in links:
            if node["id"] == link["source"] or node["id"] == link["target"]:
                connected += 1
        if connected > 0:
            engaged_nodes.append(node)

    # nodes = engaged_nodes

    interacts["nodes"] = nodes
    interacts["links"] = links

    return interacts


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
def get_most_engaged(interacts, count):
    nodes = interacts["nodes"]

    # Descending sort
    nodes.sort(key=lambda e: e['mentions'], reverse=True)

    # Take the X first
    most_engaged_nodes = nodes[:count]

    # Add user profile
    for node in most_engaged_nodes:
        user = get_user_details(node["id"])
        node["profile_image_url"] = user["profile_image_url"].replace("_normal", "_bigger")
        node["name"] = user["name"]
        node["followers_count"] = user["followers_count"]

    return most_engaged_nodes


def ceil_dt(dt, delta):
    return dt + (datetime.datetime.min - dt) % delta


# Get tweets
def get_tweets(_ids):
    tweets_data = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["tweets"]

    for _id in _ids:

        doc = col.find_one({"_id": ObjectId(_id)})

        # Iterate over tweets
        for tweet in doc["tweets"]:
            tweets_data.append(tweet)

    return tweets_data


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
        time_format = "%Y-%m-%d %H"
    elif unit == "d":
        time_format = "%Y-%m-%d"

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
