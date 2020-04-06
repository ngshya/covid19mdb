import os
from pymongo import MongoClient


def get_collection(collection, db="covid-19"):
    mdb_user = os.environ["mdb_user"]
    mdb_password = os.environ["mdb_pwd"]
    client = MongoClient('mongodb://'+mdb_user+':'+mdb_password\
        +'@ds263018.mlab.com:63018/covid-19', retryWrites=False)
    db = client[db]
    collection = db[collection]
    return collection