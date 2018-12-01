import pymongo


def db_connect():
    client = pymongo.MongoClient('mongodb://%s:%s@51.158.72.31:27017/twitter-workshop' % ("twitter-workshop", "yWH9BTt0ZCky2Gmw"))
    db = client["twitter-workshop"]
    return db
