from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .parts import TwitterQuery
from .libs import twitter
from .libs import mongodb

from datetime import datetime, timedelta


# /app/home/
@login_required(login_url='/app/login/')
def home(request):
    return render(request, 'app/home.html')


# /app/login/
@login_required(login_url='/app/login/')
def update_query(request):

    if request.is_ajax() is False:
        return -1

    _id = request.POST.get('_id')

    return JsonResponse(twitter.update_query(_id), safe=False)


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
            index.append({"id": doc["_id"], "keyword": doc["keyword"], "created": doc["created"], "count":doc["count"], "lang":doc["lang"], "updated":doc["updated"]})

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

            twitter.create_query(keyword, count, language, request.user.id)

            return HttpResponseRedirect('/app/database')
    else:
        form = TwitterQuery.TwitterQuery()

    return render(request, 'app/query.html', {'form': form})


# /app/dashboard/
# Display the list of query's tweets
@login_required(login_url='/app/login/')
def dashboard(request):

    metadata = twitter.get_metadata(request.GET['id'])

    # Date initialization
    timeframe = {}
    now = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)

    try:
        # Weird behavior on Mac (Unix?), we need to add to the current start date (+ 24*60*60)
        timeframe["current_start_date"] = datetime.utcfromtimestamp(int(request.GET['start_date'][:-3]) + 24*60*60 ).strftime("%Y-%m-%d")
    except KeyError:
        timeframe["current_start_date"] = yesterday.strftime("%Y-%m-%d")
    try:
        timeframe["current_end_date"] = datetime.utcfromtimestamp(int(request.GET['end_date'][:-3]) + 24*60*60 ).strftime("%Y-%m-%d")
    except KeyError:
        timeframe["current_end_date"] = now.strftime("%Y-%m-%d")

    timeframe["delta"] = (datetime.strptime(timeframe["current_end_date"],"%Y-%m-%d") - datetime.strptime(timeframe["current_start_date"],"%Y-%m-%d")).days

    timeframe["previous_start_date"] = (datetime.strptime(timeframe["current_start_date"], "%Y-%m-%d") - timedelta(days=timeframe["delta"])).strftime("%Y-%m-%d")
    timeframe["previous_end_date"] = timeframe["current_start_date"]

    # Getting tweets
    tweets = twitter.get_tweets(metadata["_id"])
    current_tweets = twitter.get_tweets_by_timeframe(tweets, timeframe["current_start_date"], timeframe["current_end_date"])
    previous_tweets = twitter.get_tweets_by_timeframe(tweets, timeframe["previous_start_date"], timeframe["previous_end_date"])

    # Networkx tests
    # twitter.build_network_graph(current_tweets)

    # Getting basic statistics
    current_tweets_count = twitter.get_tweets_count(current_tweets)
    current_users_count = twitter.get_users_count(current_tweets)
    current_interactions_count = twitter.get_interactions_count(current_tweets)
    current_density_count = twitter.get_density_rate(current_tweets)

    previous_tweets_count = twitter.get_tweets_count(previous_tweets)
    previous_users_count = twitter.get_users_count(previous_tweets)
    previous_interactions_count = twitter.get_interactions_count(previous_tweets)
    previous_density_count = twitter.get_density_rate(previous_tweets)

    if previous_tweets_count == 0:
        previous_tweets_count = 1
    if previous_users_count == 0:
        previous_users_count = 1
    if previous_interactions_count == 0:
        previous_interactions_count = 1
    if previous_density_count == 0:
        previous_density_count = 1

    tweets_count_variation = round(((current_tweets_count * 100) / previous_tweets_count) - 100, 2)
    tweets_users_variation = round(((current_tweets_count * 100) / previous_users_count) - 100, 2)
    tweets_interactions_variation = round(((current_interactions_count * 100) / previous_interactions_count) - 100, 2)
    tweets_density_variation = round(((current_density_count * 100) / previous_density_count) - 100, 2)

    stats = {"current_tweets_count" : current_tweets_count, "current_users_count" : current_users_count, "current_interactions_count" : current_interactions_count, "current_density_count" : current_density_count,
                  "previous_tweets_count": previous_tweets_count, "previous_users_count": previous_users_count, "previous_interactions_count": previous_interactions_count, "previous_density_count": previous_density_count,
                  "tweets_count_variation": tweets_count_variation, "tweets_users_variation": tweets_users_variation, "tweets_interactions_variation": tweets_interactions_variation, "tweets_density_variation": tweets_density_variation }

    # Getting detailed statistics (per time unit)
    if timeframe["delta"] == 1:
        time_unit = "h"
    else:
        time_unit = "d"

    current_stats = twitter.get_stats_per_time_unit(current_tweets, time_unit, timeframe["current_start_date"],timeframe["current_end_date"])
    previous_stats = twitter.get_stats_per_time_unit(previous_tweets, time_unit, timeframe["previous_start_date"],timeframe["previous_end_date"])

    detailed_stats = []

    for current_stat, previous_stat in zip(current_stats, previous_stats):
        detailed_stats.append({"current_timeframe": current_stat["timeframe"], "previous_timeframe": previous_stat["timeframe"],
                      "current_tweets_count": current_stat["tweets_count"], "previous_tweets_count": previous_stat["tweets_count"],
                      "current_users_count": current_stat["users_count"], "previous_users_count": previous_stat["users_count"],
                      "current_interactions_count": current_stat["interactions_count"], "previous_interactions_count": previous_stat["interactions_count"],
                      "current_density_count": current_stat["density_count"], "previous_density_count": previous_stat["density_count"]})

    # Correction for client's side
    timeframe["current_end_date"] = (datetime.strptime(timeframe["current_end_date"], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    timeframe["previous_end_date"] = (datetime.strptime(timeframe["previous_end_date"], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    metadata = {"id" : metadata["_id"], "keyword" : metadata["keyword"]}

    return render(request, 'app/dashboard.html', {'metadata': metadata, 'timeframe': timeframe, 'stats': stats, 'detailed_stats': detailed_stats})


# /app/interactions/
# Display interactions graph
@login_required(login_url='/app/login/')
def interactions(request):

    metadata = twitter.get_metadata(request.GET['id'])

    # Date initialization
    timeframe = {}
    now = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)

    try:
        timeframe["current_start_date"] = datetime.utcfromtimestamp(int(request.GET['start_date'][:-3])).strftime("%Y-%m-%d")
    except KeyError:
        timeframe["current_start_date"] = yesterday.strftime("%Y-%m-%d")
    try:
        timeframe["current_end_date"] = datetime.utcfromtimestamp(int(request.GET['end_date'][:-3]) + 24 * 60 * 60).strftime(
            "%Y-%m-%d")
    except KeyError:
        timeframe["current_end_date"] = now.strftime("%Y-%m-%d")

    timeframe["delta"] = (datetime.strptime(timeframe["current_end_date"], "%Y-%m-%d") - datetime.strptime(
        timeframe["current_start_date"], "%Y-%m-%d")).days

    timeframe["previous_start_date"] = (datetime.strptime(timeframe["current_start_date"], "%Y-%m-%d") - timedelta(days=timeframe["delta"])).strftime("%Y-%m-%d")
    timeframe["previous_end_date"] = timeframe["current_start_date"]

    # Getting tweets
    tweets = twitter.get_tweets(metadata["_id"])
    current_tweets = twitter.get_tweets_by_timeframe(tweets, timeframe["current_start_date"], timeframe["current_end_date"])

    # Building the interactions dict
    interactions = twitter.get_interactions(current_tweets)
    influencers = twitter.get_influencers(interactions, 3)

    # Correction for client's side
    timeframe["current_end_date"] = (
                datetime.strptime(timeframe["current_end_date"], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    timeframe["previous_end_date"] = (
                datetime.strptime(timeframe["previous_end_date"], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    metadata = {"id": metadata["_id"], "keyword": metadata["keyword"]}


    return render(request, 'app/interactions.html', {'metadata': metadata, 'timeframe':timeframe, 'interactions': interactions, 'influencers':influencers})

# Ajax calls

# /app/get_user_details/ (ajax)
# Return details of an user
@login_required(login_url='/app/login/')
def get_user_details(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    _id = request.POST.get('_id')

    return JsonResponse(twitter.get_user_details(_id), safe=False)