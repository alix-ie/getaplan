from pymongo import MongoClient
from app import app


def create_connection():
    client = MongoClient(app.config['MONGO_URI'])
    return client
