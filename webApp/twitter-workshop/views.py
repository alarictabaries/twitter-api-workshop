from django.http import HttpResponseRedirect
from django.shortcuts import render
from .parts import TwitterQuery
from .libraries import twitter
from .libraries import mongodb
from django.http import JsonResponse


# /app/home
def home(request):
    return render(request, 'app/home.html', {'user': request.user})


# /app/database
# Display a the list of created queries
def database(request):

    db = mongodb.db_connect()
    col = db["index"]
    docs = col.find()

    index = []

    for doc in docs:
        index.append([doc["_id"], doc["keyword"], doc["created_at"], doc["options"]["count"], doc["options"]["lang"]])

    index = reversed(index)

    return render(request, 'app/database.html', {'index': index})


# /app/query
# Create a query
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

    return render(request, 'app/query.html', {'form': form})


# /app/dataset
# Display the list of query's tweets
def dataset(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets = twitter.get_tweets(metadata["_id"])

    print(twitter.get_stats_per_time_unit(tweets, "h"))

    metadata = [metadata["_id"], metadata["keyword"]]

    return render(request, 'app/dataset.html', {'metadata': metadata})


# /app/interactions
# Display interactions graph
def interactions(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets = twitter.get_tweets(metadata["_id"])
    interactions = twitter.get_interactions(tweets)

    metadata = [metadata["_id"], metadata["keyword"]]

    influencers = twitter.get_influencers(interactions, 3)

    return render(request, 'app/interactions.html', {'metadata': metadata, 'interactions': [interactions, influencers]})


# Ajax calls

# /app/update_interactions (ajax)
# Update interactions graph
def update_interactions(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    # Initialize options
    id = request.POST.get('id')

    interactions = {}

    return JsonResponse(interactions, safe=False)


# /app/get_user_details (ajax)
# Return details of an user
def get_user_details(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    _id = request.POST.get('_id')

    return JsonResponse(twitter.get_user_details(_id), safe=False)