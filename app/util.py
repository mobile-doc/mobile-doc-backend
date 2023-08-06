import pymongo
import os
import logging

atlas_password = os.getenv("_ATLAS_PASSWORD")
atlas_username = os.getenv("_ATLAS_USERNAME")

client = pymongo.MongoClient(
    f"mongodb+srv://{atlas_username}:{atlas_password}@cluster0.ds5ggbq.mongodb.net/?retryWrites=true&w=majority"
)


def get_db():
    return client.get_database("main_db")


class CustomLogger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def info(self, message):
        self.logger.info(message)
        print("INFO:\t", message)

    def error(self, message):
        self.logger.error(message)
        print("ERROR:\t", message)

    def warning(self, message):
        self.logger.warning(message)
        print("WARNING:\t", message)


custon_logger = CustomLogger()
