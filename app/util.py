import pymongo
import os
import logging
import redis
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext
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


def get_redis_client():
    custon_logger.info("Instantiating Redis Client")
    try:
        redis_client = redis.Redis(
            host="redis-13803.c124.us-central1-1.gce.cloud.redislabs.com",
            port=13803,
            password=os.getenv("_REDIS_PASSWORD"),
        )
        return redis_client
    except Exception as e:
        custon_logger.error(f"Error with Redis Client: {e}")
        return None


redis_client = get_redis_client()


# authentication
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "temp_secret_key"
JWT_REFRESH_SECRET_KEY = "temp_secret_key"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt
