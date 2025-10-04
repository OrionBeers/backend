import pymongo
import certifi

mongo_user="hackthon_db_user"
mongo_password="PbxrIr1JJ28va5vz"
mongo_cluser="hackthon"

def connect():

    client = pymongo.MongoClient(
        f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_cluser}.mvocxqr.mongodb.net/?retryWrites=true&w=majority&appName=hackthon", tlsCAFile=certifi.where()
    )

    return client['hackthon']