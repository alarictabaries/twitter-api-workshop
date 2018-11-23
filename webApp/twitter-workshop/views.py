from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import pandas as pd
import json
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

    interactions = {}
    nodes = []
    links = []

    with open("twitter-workshop/tmp/" + file) as json_data:
        data = json.load(json_data)
        for tweet in data:
            tmp_node = {}
            tmp_node["id"] = tweet["user"]["id"]
            tmp_node["alias"] = tweet["user"]["screen_name"]
            tmp_node["type"] = 1 # 1 for author (active)
            nodes.append(tmp_node)
            for user in tweet['entities']['user_mentions']:
                if user:
                    tmp_node = {}
                    tmp_link = {}
                    tmp_link["source"] = tweet["user"]["id"]
                    tmp_link["target"] = user['id']
                    tmp_link["value"] = 1
                    tmp_node["id"] = user['id']
                    tmp_node["alias"] = user["screen_name"]
                    tmp_node["type"] = 2  # 2 for mention (inactive)
                    nodes.append(tmp_node)
                    links.append(tmp_link)
        json_data.close()

        unique_nodes = []
        for node in nodes :
            duplicated = 0
            tmp_node = {}
            tmp_node["id"] = node["id"]
            tmp_node["alias"] = node["alias"]
            tmp_node["type"] = node["type"]
            for unique_node in unique_nodes:
                if(node["id"] == unique_node["id"]) and (node["type"] == unique_node["type"]):
                    duplicated += 1
            if duplicated == 0:
                unique_nodes.append(tmp_node)

        # Unique links ? what if a same user tweets 5 times "@mention wtf", should we keep it?

        unique_links = []
        for link in links:
            duplicated = 0
            tmp_link = {}
            tmp_link["source"] = link["source"]
            tmp_link["target"] = link["target"]
            tmp_link["value"] = link["value"]
            for unique_link in unique_links:
                if (link["source"] == unique_link["source"]) and (link["target"] == unique_link["target"]):
                    duplicated += 1
            if duplicated == 0:
                unique_links.append(tmp_link)

        nodes = unique_nodes
        links = unique_links

        interactions["nodes"] = nodes
        interactions["links"] = links

    return render(request, 'visualize.html', {'header': header, 'interactions': interactions})