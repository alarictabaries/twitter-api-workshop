from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import re

from .parts import TwitterQuery

from .libraries import twitter
from .libraries import dir
from .libraries import csv

import json


# /
def index(request):
    return render(request, 'index.html')


# /database
def data_base(request):
    data_base = csv.get_data("twitter-workshop/tmp/database.csv", ["seed","filename","query","count", "rt", "lang","creation_date"])
    data_base.reverse()
    return render(request, 'data_base.html', {'database': data_base})


# /query
def query(request):
    if request.method == 'POST':
        form = TwitterQuery.TwitterQuery(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            count = form.cleaned_data['count']
            rt = form.cleaned_data['rt']
            language = form.cleaned_data['language']
            seed = twitter.scrape_twitter(subject, count, rt, language)

            return HttpResponseRedirect('data_base')
    else:
        form = TwitterQuery.TwitterQuery()

    return render(request, 'query.html', {'form': form})


# /data_set
def data_set(request):
    file = "tweets_" + request.GET['seed'] + ".json"
    data_base = csv.get_data("twitter-workshop/tmp/database.csv",
                            ["seed", "filename", "query", "count", "rt", "lang", "creation_date"])
    header = []
    for row in data_base:
        if row[0] == request.GET['seed']:
            header = row

    tweet_data = []
    with open("twitter-workshop/tmp/" + file) as json_data:
        data = json.load(json_data)
        for tweet in data:
            short_text = (tweet["full_text"][:125] + '..') if len(tweet["full_text"]) > 125 else tweet["full_text"]
            tweet_data.append([tweet["full_text"], short_text, tweet["id_str"], tweet["user"]["screen_name"], tweet["user"]["id_str"], tweet["created_at"]])
        json_data.close()

    # data : full_text, short_text, id_str, alias, alias_id, created_at
    return render(request, 'data_set.html', {'header': header, 'data': tweet_data})


# /download_json
def download_json(request):
    file = "tweets_" + request.GET['seed'] + ".json"

    file_path = "twitter-workshop/tmp/" + file
    FilePointer = open(file_path, "r")

    response = HttpResponse(FilePointer, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=' + file

    return response


# /visualize
def visualize(request):

    file = "tweets_" + request.GET['seed'] + ".json"
    data_base = csv.get_data("twitter-workshop/tmp/database.csv",
                             ["seed", "filename", "query", "count", "rt", "lang", "creation_date"])

    header = []
    for row in data_base:
        if row[0] == request.GET['seed']:
            header = row

    entities = []

    with open("twitter-workshop/tmp/" + file) as json_data:
        data = json.load(json_data)
        for tweet in data:
            mentions = []
            for user in tweet['entities']['user_mentions']:
                if user:
                    mentions.append([user['id_str'], user['screen_name']])
            entities.append([tweet["user"]["screen_name"], tweet["user"]["id_str"], mentions])
        json_data.close()

    engaged_entities = []
    tmp_entities = []

    for tweet in entities:
        for engaged in tweet[2]:
            if engaged[0] in tmp_entities:
                index = tmp_entities.index(engaged[0])
                engaged_entities[index][2] = engaged_entities[index][2] + 1
            else:
                tmp_entities.append(engaged[0])
                engaged_entities.append([engaged[0], engaged[1], 1])

        engaged_entities = sorted(engaged_entities, key=lambda x: x[2], reverse=True)

        # top can be reworked
        # it actually return the 15 first without paying attention to the count column
        top_engaged_entities = engaged_entities[:15]

    return render(request, 'visualize.html', {'header': header, 'entities': top_engaged_entities})