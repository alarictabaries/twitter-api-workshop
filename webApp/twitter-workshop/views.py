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
            index.append([doc["_id"], doc["keyword"], doc["created"], doc["count"], doc["lang"], doc["updated"]])

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

    current_stats = twitter.get_stats_per_time_unit(twitter.get_tweets_by_timeframe(tweets, "2018-12-29 00:00", "2018-12-30 00:00"), "h")

    stats_f = []

    for current_stat in current_stats:
        stats_f.append({"timeframe": current_stat["timeframe"], "current_tweets_count": int(current_stat["tweets_count"]*1.9), "comparison_tweets_count": current_stat["tweets_count"]})

    metadata = [metadata["_id"], metadata["keyword"]]

    return render(request, 'app/dataset.html', {'metadata': metadata, 'stats': stats_f })


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