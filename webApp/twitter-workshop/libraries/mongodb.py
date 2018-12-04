# Generic operations with mongoDB

import pymongo


# Connecting to MongoDB instance
# IP of distant instance : 192.168.235.128:27017
def db_connect():
    client = pymongo.MongoClient('mongodb://%s:%s@51.158.72.31:27017/twitter-workshop' % ("twitter-workshop", "yWH9BTt0ZCky2Gmw"))
    db = client["twitter-workshop"]
    return db
