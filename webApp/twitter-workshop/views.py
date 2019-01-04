from django.http import HttpResponseRedirect
from django.shortcuts import render
from .parts import TwitterQuery
from .libs import twitter
from .libs import mongodb
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from pprint import pprint


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


# /app/dataset/
# Display the list of query's tweets
@login_required(login_url='/app/login/')
def dataset(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets = twitter.get_tweets(metadata["_id"])
    current_tweets = twitter.get_tweets_by_timeframe(tweets, "2018-12-30 00:00", "2018-12-31 00:00")
    previous_tweets = twitter.get_tweets_by_timeframe(tweets, "2018-12-29 00:00", "2018-12-30 00:00")

    current_tweets_count = twitter.get_tweets_count(current_tweets)
    current_users_count = twitter.get_users_count(current_tweets)
    current_interactions_count = twitter.get_interactions_count(current_tweets)

    previous_tweets_count = twitter.get_tweets_count(previous_tweets)
    previous_users_count = twitter.get_users_count(previous_tweets)
    previous_interactions_count = twitter.get_interactions_count(previous_tweets)

    stats = {"current_tweets_count" : current_tweets_count, "current_users_count" : current_users_count, "current_interactions_count" : current_interactions_count,
                  "previous_tweets_count": previous_tweets_count, "previous_users_count": previous_users_count, "previous_interactions_count": previous_interactions_count,
                  "tweets_count_variation": round(((current_tweets_count*100)/previous_tweets_count)-100, 2), "tweets_users_variation": round(((current_users_count*100)/previous_users_count)-100, 2), "tweets_interactions_variation": round(((current_interactions_count*100)/previous_interactions_count)-100, 2) }


    current_stats = twitter.get_stats_per_time_unit(current_tweets, "h")
    previous_stats = twitter.get_stats_per_time_unit(previous_tweets, "h")

    detailed_stats = []
    for current_stat, previous_stat in zip(current_stats, previous_stats):
        detailed_stats.append({"current_timeframe": current_stat["timeframe"], "previous_timeframe": previous_stat["timeframe"],
                      "current_tweets_count": current_stat["tweets_count"], "previous_tweets_count": previous_stat["tweets_count"],
                      "current_users_count": current_stat["users_count"], "previous_users_count": previous_stat["users_count"],
                      "current_interactions_count": current_stat["interactions_count"], "previous_interactions_count": previous_stat["interactions_count"]})

    metadata = {"id" : metadata["_id"], "keyword" : metadata["keyword"]}

    return render(request, 'app/dataset.html', {'metadata': metadata, 'stats': stats, 'detailed_stats': detailed_stats})


# /app/interactions/
# Display interactions graph
@login_required(login_url='/app/login/')
def interactions(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets = twitter.get_tweets(metadata["_id"])
    interactions = twitter.get_interactions(tweets)

    metadata = {"id" : metadata["_id"], "keyword": metadata["keyword"]}

    influencers = twitter.get_influencers(interactions, 3)

    return render(request, 'app/interactions.html', {'metadata': metadata, 'interactions': [interactions, influencers]})


# /app/home/
@login_required(login_url='/app/login/')
def update_query(request):

    if request.is_ajax() is False:
        return -1

    _id = request.POST.get('_id')

    return JsonResponse(twitter.update_query(_id), safe=False)

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