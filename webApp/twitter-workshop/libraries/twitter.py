# Operations with Twitter's API

import tweepy
from . import mongodb
import datetime
import pytz
from bson.objectid import ObjectId


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
    _tweets = col.insert_one({"tweets": []})

    for tweet in tweepy.Cursor(api.search, q=keyword, lang=lang, tweet_mode='extended', result_type="recent",include_entities=True).items(count):
        col.update_one({'_id': _tweets.inserted_id}, {'$push': {'tweets': tweet._json}})

    col = db["index"]

    # Write metadata
    col.insert_one({
        "keyword": keyword,
        "options": {
            "count": count,
            "lang": lang,
        },
        "_tweets": _tweets.inserted_id,
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
def get_tweets(_id):
    tweet_data = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["tweets"]
    doc = col.find_one({"_id": ObjectId(_id)})

    # Iterate over tweets
    for tweet in doc["tweets"]:
        short_text = (tweet["full_text"][:125] + '..') if len(tweet["full_text"]) > 125 else tweet["full_text"]
        datetime_obj = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        datetime_obj = datetime_obj.replace(tzinfo=pytz.timezone('UTC'))
        datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
        tweet_data.append(
            [tweet["full_text"], short_text, tweet["id_str"], tweet["user"]["screen_name"], tweet["user"]["id_str"],
             datetime_obj])

    return tweet_data


# Get interactions
def get_interactions(_id, **options):

    # If options are set
    start_date = options.get('start_date', None)
    end_date = options.get('end_date', None)
    simplified = options.get('simplified', None)

    interactions = {}
    nodes = []
    links = []

    # Read the tweets document
    db = mongodb.db_connect()
    col = db["tweets"]
    doc = col.find_one({"_id": ObjectId(_id)})

    # Iterate over tweets
    for tweet in doc["tweets"]:
        datetime_obj = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
        datetime_obj = datetime_obj.replace(tzinfo=pytz.timezone('UTC'))
        datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
        tmp_node = {"id": tweet["user"]["id"], "id_str": tweet["user"]["id_str"],
                    "alias": tweet["user"]["screen_name"], "type": 1, "freq": 0}
        # If date is set
        if start_date:
            # If the tweet is in the specified time frame
            if (datetime.datetime.strptime(datetime_obj, "%Y-%m-%d %H:%M") >= datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M")) and (datetime.datetime.strptime(datetime_obj, "%Y-%m-%d %H:%M") <= datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M")):
                nodes.append(tmp_node)
        else:
            nodes.append(tmp_node)

        # Iterate over mentions
        for user in tweet['entities']['user_mentions']:
            if user and (user['id'] != tweet["user"]["id"]): # The user can't mention himself
                tmp_node = {"id": user['id'], "id_str": user['id_str'], "alias": user["screen_name"], "type": 2,"freq": 0}
                tmp_link = {"source": tweet["user"]["id"], "target": user['id'], "value": 1}
                # If date is set
                if start_date:
                    # If the tweet is in the specified time frame
                    if (datetime.datetime.strptime(datetime_obj, "%Y-%m-%d %H:%M") >= datetime.datetime.strptime(
                            start_date, "%Y-%m-%d %H:%M")) and (
                            datetime.datetime.strptime(datetime_obj, "%Y-%m-%d %H:%M") <= datetime.datetime.strptime(
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
            tmp_node = {"id": node["id"], "id_str": node["id_str"], "alias": node["alias"], "type": node["type"],
                        "freq": node["freq"]}
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
                node["freq"] += 1

    engaged_nodes = []
    engaged_links = []

    # If simplified is set
    threshold = 0
    if simplified:
        threshold = 1

    # Remove not connected nodes and superfluous nodes
    # Superfluous : small nodes (<1 mentioned) or has only one link
    for node in nodes:
        link_stroke = 0
        connected = 0
        for link in links:
            if (node["id"] == link["source"]) and (node["freq"] >= threshold):
                link_stroke += 1
                engaged_links.append({"source": link["source"], "target": link["target"], "value": link_stroke})
            if (node["id"] == link["source"]) or (node["id"] == link["target"]) and (node["freq"] >= threshold):
                connected += 1
        if connected > 0:
            engaged_nodes.append(node)

    links = engaged_links
    nodes = engaged_nodes

    # Chrome sorting automatically JS objects so we're fucked
    # nodes.sort(key=lambda e: e['freq'], reverse=False)

    interactions["nodes"] = nodes
    interactions["links"] = links

    return interactions


# Define X (count) most engaged nodes in an interactions list
def get_most_engaged(interactions, count):

    nodes = interactions["nodes"]

    # Descending sort
    nodes.sort(key=lambda e: e['freq'], reverse=True)
    # Take the X first
    most_engaged_nodes = nodes[:count]

    return most_engaged_nodes
