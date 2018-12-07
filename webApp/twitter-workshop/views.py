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
# Display a the list of created queries
def database(request):

    db = mongodb.db_connect()
    col = db["index"]
    docs = col.find()

    index = []

    for doc in docs:
        index.append([doc["_id"], doc["keyword"], doc["created_at"], doc["options"]["count"], doc["options"]["lang"]])

    index = reversed(index)

    return render(request, 'database.html', {'index': index})


# /query
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

    return render(request, 'query.html', {'form': form})


# /dataset
# Display the list of query's tweets
def dataset(request):

    metadata = twitter.get_metadata(request.GET['id'])
    tweets_distribution = twitter.get_tweets_distribution(metadata["_tweets"])
    twitter.get_tweets_distribution(metadata["_tweets"])

    metadata = [metadata["_id"], metadata["_tweets"], metadata["keyword"]]


    return render(request, 'dataset.html', {'metadata': metadata, 'distribution': tweets_distribution})


# /interactions
# Display interactions graph
def interactions(request):

    metadata = twitter.get_metadata(request.GET['id'])
    interactions = twitter.get_interactions(metadata["_tweets"])
    metadata = [metadata["_id"], metadata["_tweets"], metadata["keyword"]]

    most_engaged_nodes = twitter.get_most_engaged(interactions, 3)

    return render(request, 'interactions.html', {'metadata': metadata, 'interactions': [interactions, most_engaged_nodes]})


# Ajax calls

# /update_interactions (ajax)
# Update interactions graph
def update_interactions(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    # Initialize options
    id = request.POST.get('id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    threshold = int(request.POST.get('threshold'))

    # Read metadata
    metadata = twitter.get_metadata(id)

    # Update interactions list and most engaged nodes
    interacts = twitter.get_interactions(metadata["_tweets"], start_date=start_date, end_date=end_date, threshold=threshold)
    most_engaged_nodes = twitter.get_most_engaged(interacts, 3)

    interacts = [interacts, most_engaged_nodes]

    return JsonResponse(interacts, safe=False)


# /get_user_details (ajax)
# Rerturn details of an user
def get_user_details(request):

    # Check if request is called from ajax
    if request.is_ajax() is False:
        return -1

    _id = request.POST.get('_id')

    return JsonResponse(twitter.get_user_details(_id), safe=False)