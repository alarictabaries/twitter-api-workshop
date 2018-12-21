from django.http import HttpResponseRedirect
from django.shortcuts import render
from .parts import TwitterQuery
from .libs import twitter
from .libs import mongodb
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# /app/home/
@login_required(login_url='/app/login/')
def home(request):
    return render(request, 'app/home.html')


# /app/database/
# Display a the list of created queries
@login_required(login_url='/app/login/')
def database(request):

    db = mongodb.db_connect()
    col = db["app_queries"]
    docs = col.find()

    index = []

    for doc in docs:
        if doc["_user"] == request.user.id :
            index.append([doc["_id"], doc["keyword"], doc["created_at"], doc["options"]["count"], doc["options"]["lang"]])

    index = reversed(index)

    return render(request, 'app/database.html', {'index': index})


# /app/query/
# Create a query
@login_required(login_url='/app/login/')
def query(request):

    if request.method == 'POST':
        form = TwitterQuery.TwitterQuery(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            count = form.cleaned_data['count']
            language = form.cleaned_data['language']

            twitter.scrape_twitter(keyword, count, language, request.user.id)

            return HttpResponseRedirect('database')
    else:
        form = TwitterQuery.TwitterQuery()

    return render(request, 'app/query.html', {'form': form})


# /app/dataset/
# Display the list of query's tweets
@login_required(login_url='/app/login/')
def dataset(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets = twitter.get_tweets(metadata["_id"])

    tweets = twitter.get_tweets_by_timeframe(tweets, "2018-12-13 00:00", "2018-12-14 00:00")

    print(twitter.get_stats_per_time_unit(tweets, "d"))

    metadata = [metadata["_id"], metadata["keyword"]]

    return render(request, 'app/dataset.html', {'metadata': metadata})


# /app/interactions/
# Display interactions graph
@login_required(login_url='/app/login/')
def interactions(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets = twitter.get_tweets(metadata["_id"])
    interactions = twitter.get_interactions(tweets)

    metadata = [metadata["_id"], metadata["keyword"]]

    influencers = twitter.get_influencers(interactions, 3)

    return render(request, 'app/interactions.html', {'metadata': metadata, 'interactions': [interactions, influencers]})


# Ajax calls

# /app/update_interactions/ (ajax)
# Update interactions graph
@login_required(login_url='/app/login/')
def update_interactions(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    # Initialize options
    id = request.POST.get('id')

    interactions = {}

    return JsonResponse(interactions, safe=False)


# /app/get_user_details/ (ajax)
# Return details of an user
@login_required(login_url='/app/login/')
def get_user_details(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    _id = request.POST.get('_id')

    return JsonResponse(twitter.get_user_details(_id), safe=False)