# Operations with Twitter's API

import tweepy
import uuid
import datetime
import json
import os.path
from . import csv
import datetime
import pytz
import sys


# Create random string
def random_seed(length):
    return uuid.uuid4().hex[:length].upper()


# Save tweets meeting the criteria to a CSV file
def scrape_twitter(query, count, rt, lang):
    seed = random_seed(8)
    date_now = datetime.datetime.now()

    query_file = "tweets_" + seed + ".json"
    tweets = []

    auth = tweepy.OAuthHandler('y3fvWam4738fGFCSuVJpIhtwp', 'czDAPY4XnYe4fp4n6FMwrHSFGtF0nY15PgnmozeBAsnObHiKJr')
    auth.set_access_token('229596006-BzKTTM85v2Ca0xf7d11CPM7AKhIOnx03EsUNjgsk',
                          'FnyvhnqiKtRCroJ1iX1qaLxtrn7uEDgXONGplAxZv230V')
    api = tweepy.API(auth, wait_on_rate_limit=True)

    if rt:
        for tweet in tweepy.Cursor(api.search, q=query, lang=lang, tweet_mode='extended', result_type="recent",
                                   include_entities=True).items(count):
            tweets.append(tweet._json)
    else:
        for tweet in tweepy.Cursor(api.search, q=query + '-filter:retweets', lang=lang, tweet_mode='extended',
                                   result_type="recent", include_entities=True).items(count):
            tweets.append(tweet._json)
    csv.append_csv("twitter-workshop/tmp/database.csv",
                   [seed, query_file, query, count, rt, lang, date_now.strftime("%Y-%m-%d %H:%M")])

    with open("twitter-workshop/tmp/" + query_file, 'w') as outfile:
        json.dump(tweets, outfile, indent=4, sort_keys=True)
        outfile.close()
    return seed


def get_interactions(seed):

    debug = False

    # Caching system
    if (os.path.isfile('twitter-workshop/tmp/interactions_' + seed + '.json')) and (debug == False):
        json_data = json.loads(open('twitter-workshop/tmp/interactions_' + seed + '.json').read())
        return json_data;

    interactions = {}
    nodes = []
    links = []

    with open("twitter-workshop/tmp/tweets_" + seed + ".json") as json_data:
        data = json.load(json_data)
        for tweet in data:
            tmp_node = {"id": tweet["user"]["id"], "id_str": tweet["user"]["id_str"],
                        "alias": tweet["user"]["screen_name"], "type": 1, "freq": 1}
            nodes.append(tmp_node)
            for user in tweet['entities']['user_mentions']:
                if user:
                    tmp_node = {"id": user['id'], "id_str": user['id_str'], "alias": user["screen_name"], "type": 2,
                                "freq": 1}
                    tmp_link = {"source": tweet["user"]["id"], "target": user['id'], "value": 1}
                    nodes.append(tmp_node)
                    links.append(tmp_link)
        json_data.close()

        unique_nodes = []
        for node in nodes:
            duplicated = 0
            active = 0
            for unique_node in unique_nodes:
                if node["id"] == unique_node["id"]:
                    duplicated += 1
                if (node["id"] == unique_node["id"]) and (node["type"] == 1):
                    active += 1

            if duplicated == 0:
                tmp_node = {"id": node["id"], "id_str": node["id_str"], "alias": node["alias"], "type": node["type"],
                            "freq": node["freq"]}
                unique_nodes.append(tmp_node)

            for unique_node in unique_nodes:
                if active > 0:
                    if unique_node["id"] == node["id"]:
                        unique_node["type"] = 1

        # Unique links ? what if a same user tweets 5 times "@mention wtf", should we keep it?

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

        for link in unique_links:
            for node in nodes:
                if node["id"] == link["target"]:
                    node["freq"] += 1

        # engaged_nodes = []

        # Removing not connected nodes
        # for node in nodes:
        #     connected = 0
        #     for link in links:
        #         if (node["id"] == link["source"]) or node["id"] == link["target"]:
        #             connected += 1
        #     if connected > 0:
        #         engaged_nodes.append(node)

        #nodes = engaged_nodes

        interactions["nodes"] = nodes
        interactions["links"] = links

        with open('twitter-workshop/tmp/interactions_' + seed + ".json", 'w') as outfile:
            json.dump(interactions, outfile, indent=4, sort_keys=True)

    return interactions


def get_tweets(seed):
    tweet_data = []

    with open("twitter-workshop/tmp/tweets_" + seed + ".json") as json_data:
        data = json.load(json_data)
        for tweet in data:
            short_text = (tweet["full_text"][:125] + '..') if len(tweet["full_text"]) > 125 else tweet["full_text"]
            datetime_obj = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
            datetime_obj = datetime_obj.replace(tzinfo=pytz.timezone('UTC'))
            datetime_obj = datetime_obj.strftime("%Y-%m-%d %H:%M")
            tweet_data.append([tweet["full_text"], short_text, tweet["id_str"], tweet["user"]["screen_name"], tweet["user"]["id_str"],datetime_obj])
    json_data.close()

    return tweet_data

def get_most_engaged(interactions, count):
    nodes = interactions["nodes"]

    nodes.sort(key=lambda e: e['freq'], reverse=True)

    most_engaged_nodes =  nodes[:count]

    return most_engaged_nodes