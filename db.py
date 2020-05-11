from flask import Flask
from flask_pymongo import pymongo
from app import app
CONNECTION_STRING = "mongodb+srv://admin:13579@cluster0-prci1.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('recycling_app')
place_collection = pymongo.collection.Collection(db, 'place')
post_collection = pymongo.collection.Collection(db, 'post')
