from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
import re

from .parts import TwitterQuery

from .libraries import twitter
from .libraries import dir
from .libraries import csv


# /
def index(request):
    return render(request, 'index.html')


# /database
def data_base(request):
    data_base = csv.get_data("twitter-workshop/tmp/database.csv", ["seed","filename","query","count","lang","creation_date"])
    data_base.reverse()
    return render(request, 'data_base.html', {'database': data_base})


# /query
def query(request):
    if request.method == 'POST':
        form = TwitterQuery.TwitterQuery(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            count = form.cleaned_data['count']
            language = form.cleaned_data['language']
            seed = twitter.scrape_twitter(subject, count, language)

            return HttpResponseRedirect('data_base')
    else:
        form = TwitterQuery.TwitterQuery()

    return render(request, 'query.html', {'form': form})


# /data_set
def data_set(request):
    file = "tweets_" + request.GET['seed'] + ".csv"
    data_base = csv.get_data("twitter-workshop/tmp/database.csv",
                            ["seed", "filename", "query", "count", "lang", "creation_date"])
    header = []
    for row in data_base:
        if row[0] == request.GET['seed']:
            header = row

    print(header)

    data = csv.get_data("twitter-workshop/tmp/" + file, ["full_text", "id_str", "created_at", "author"])
    for row in data:
        short_text = (row[0][:125] + '..') if len(row[0]) > 125 else row[0]
        alias_json = row[3]
        alias = re.search("'screen_name': '(.*)', 'location':", alias_json)
        alias = alias.group(1)
        alias_id = re.search("'id_str': '(.*)', 'name':", alias_json)
        alias_id = alias_id.group(1)
        row.insert(1, short_text)
        row.insert(3, alias)
        row.insert(4, alias_id)
        row.pop(6)
    url = "download_csv?seed=" + request.GET['seed']

    # data : full_text, short_text, id_str, alias, alias_id, created_at
    return render(request, 'data_set.html', {'header': header, 'data': data, 'url':url})


# /download_csv
def download_csv(request):
    file = "tweets_" + request.GET['seed'] + ".csv"

    csv = pd.read_csv("twitter-workshop/tmp/" + file)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + file

    csv.to_csv(path_or_buf=response, sep=';', float_format='%.2f', index=False, decimal=",")
    return response
