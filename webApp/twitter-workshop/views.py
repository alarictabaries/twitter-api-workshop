from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse

from .parts import TwitterQuery

from .libraries import twitter
from .libraries import csv
from django.http import JsonResponse


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

    tweet_data = twitter.get_tweets(request.GET['seed'])

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


# /interactions
def interactions(request):

    file = "tweets_" + request.GET['seed'] + ".json"
    data_base = csv.get_data("twitter-workshop/tmp/database.csv",
                             ["seed", "filename", "query", "count", "rt", "lang", "creation_date"])

    header = []
    for row in data_base:
        if row[0] == request.GET['seed']:
            header = row

    interactions = twitter.get_interactions(request.GET['seed'], None, None)
    most_engaged_nodes = twitter.get_most_engaged(interactions, 5)

    return render(request, 'interactions.html', {'header': header, 'interactions': [interactions, most_engaged_nodes]})


# /update_interactions (ajax)
def update_interactions(request):

    start_time = request.POST['start_time']
    end_time = request.POST['end_time']

    interactions = twitter.get_interactions(request.GET['seed'], start_time, end_time)
    most_engaged_nodes = twitter.get_most_engaged(interactions, 5)

    interactions = [interactions, most_engaged_nodes]

    return JsonResponse(interactions, safe=False)