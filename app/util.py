import pymongo
import os
import logging
import redis
from .constants import VERSION_NAME

# database

atlas_password = os.getenv("_ATLAS_PASSWORD")
atlas_username = os.getenv("_ATLAS_USERNAME")

client = pymongo.MongoClient(
    f"mongodb+srv://{atlas_username}:{atlas_password}@cluster0.ds5ggbq.mongodb.net/?retryWrites=true&w=majority"
)


def get_db():
    return client.get_database("main_db")


# logger


class CustomLogger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def info(self, message):
        self.logger.info(message)
        if VERSION_NAME == "dev":
            print("INFO:\t", message)

    def error(self, message):
        self.logger.error(message)
        if VERSION_NAME == "dev":
            print("ERROR:\t", message)

    def warning(self, message):
        self.logger.warning(message)
        if VERSION_NAME == "dev":
            print("WARNING:\t", message)


custon_logger = CustomLogger()


# Redis for caching

redis_client = redis.Redis(
    host="redis-13803.c124.us-central1-1.gce.cloud.redislabs.com",
    port=13803,
    password=os.getenv("_REDIS_PASSWORD"),
)
