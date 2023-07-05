from config import setting
from pymongo import MongoClient


def get_database():
    connection_string = setting.MONGO_CONNECTION_STRING
    client = MongoClient(connection_string)
    database = client[setting.MONGO_DATABASE]

    return database
