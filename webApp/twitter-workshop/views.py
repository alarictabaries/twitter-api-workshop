from django.http import HttpResponseRedirect
from django.shortcuts import render

from .parts import TwitterQuery

from .libraries import twitter
from .libraries import mongodb
from django.http import JsonResponse


# /
def index(request):
    return render(request, 'index.html')


# /database
def database(request):

    db = mongodb.db_connect()
    col = db["index"]
    docs = col.find()

    index = []

    for doc in docs:
        print(doc["_id"])
        index.append([doc["_id"], doc["keyword"], doc["created_at"], doc["options"]["count"], doc["options"]["lang"]])

    index = reversed(index)

    return render(request, 'database.html', {'index': index})


# /query
def query(request):
    if request.method == 'POST':
        form = TwitterQuery.TwitterQuery(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            count = form.cleaned_data['count']
            language = form.cleaned_data['language']

            twitter.scrape_twitter(keyword, count, language)

            return HttpResponseRedirect('database')
    else:
        form = TwitterQuery.TwitterQuery()

    return render(request, 'query.html', {'form': form})


# /dataset
def dataset(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweet_data = twitter.get_tweets(metadata["_tweets"])
    metadata = [metadata["_id"], metadata["_tweets"], metadata["keyword"]]

    # data : full_text, short_text, id_str, alias, alias_id, created_at
    return render(request, 'dataset.html', {'metadata': metadata, 'data': tweet_data})


# /interactions
def interactions(request):

    metadata = twitter.get_metadata(request.GET['id'])
    interactions = twitter.get_interactions(metadata["_tweets"])
    metadata = [metadata["_id"], metadata["_tweets"], metadata["keyword"]]

    most_engaged_nodes = twitter.get_most_engaged(interactions, 3)

    return render(request, 'interactions.html', {'metadata': metadata, 'interactions': [interactions, most_engaged_nodes]})


# /update_interactions (ajax)
def update_interactions(request):

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    simplified = request.POST.get('simplified')

    metadata = twitter.get_metadata(request.GET['id'])

    interactions = twitter.get_interactions(metadata["_tweets"], start_date=start_date, end_date=end_date, simplified=simplified)
    most_engaged_nodes = twitter.get_most_engaged(interactions, 3)

    interactions = [interactions, most_engaged_nodes]

    return JsonResponse(interactions, safe=False)