import pymongo
import os


atlas_password = os.getenv("_ATLAS_PASSWORD")
atlas_username = os.getenv("_ATLAS_USERNAME")

atlas_password = "1234" if atlas_password is None else atlas_password
atlas_username = "user" if atlas_username is None else atlas_username

client = pymongo.MongoClient(
    f"mongodb+srv://{atlas_username}:{atlas_password}@cluster0.ds5ggbq.mongodb.net/?retryWrites=true&w=majority"
)

db = client.get_database("main_db")


def get_db():
    return db
