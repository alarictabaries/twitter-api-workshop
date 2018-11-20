# Operations with Twitter's API

import tweepy
import pandas as pd
import uuid
import datetime
import json
from . import csv


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
        json.dump(tweets, outfile)
        outfile.close()
    return seed


def get_mentions(id_author, entities):

    return()