# Operations with Twitter's API

import tweepy
import pandas as pd
import uuid
import datetime

from . import csv


# Create random string
def random_seed(length):
    return uuid.uuid4().hex[:length].upper()


# Save tweets meeting the criteria to a CSV file
def scrape_twitter(query, count, lang):

    seed = random_seed(8)
    date_now = datetime.datetime.now()

    query_file = "tweets_" + seed + ".csv"
    tweets = []

    auth = tweepy.OAuthHandler('y3fvWam4738fGFCSuVJpIhtwp', 'czDAPY4XnYe4fp4n6FMwrHSFGtF0nY15PgnmozeBAsnObHiKJr')
    auth.set_access_token('229596006-BzKTTM85v2Ca0xf7d11CPM7AKhIOnx03EsUNjgsk',
                          'FnyvhnqiKtRCroJ1iX1qaLxtrn7uEDgXONGplAxZv230V')
    api = tweepy.API(auth, wait_on_rate_limit=True)

    debug = 0

    for tweet in tweepy.Cursor(api.search, q=query + '-filter:retweets', lang=lang, tweet_mode='extended', result_type="recent", include_entities=True).items(count):
        tweets.append(tweet)
        debug += 1
        print(date_now.strftime("%H:%M:%S"), end=" : ")
        print(debug)

    tweets_df = pd.DataFrame(vars(tweets[i]) for i in range(len(tweets)))
    tweets_df.to_csv("twitter-workshop/tmp/" + query_file)
    csv.append_csv("twitter-workshop/tmp/database.csv", [seed, query_file, query, count, lang, date_now.strftime("%Y-%m-%d %H:%M")])

    return seed
