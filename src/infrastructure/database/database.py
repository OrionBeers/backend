import pymongo
import certifi
import os

mongo_user="hackthon_db_user"
mongo_password="PbxrIr1JJ28va5vz"
mongo_cluster="hackthon"


# mongo_user = os.environ.get("MONGO_USER")
# mongo_password = os.environ.get("MONGO_PASSWORD")
# mongo_cluster = os.environ.get("MONGO_CLUSTER")


def connect():

    client = pymongo.MongoClient(
        f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_cluster}.mvocxqr.mongodb.net/?retryWrites=true&w=majority&appName=hackthon", tlsCAFile=certifi.where()
    )

    return client[mongo_cluster]