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


custom_logger = CustomLogger()


# Redis for caching


def get_redis_client():
    custom_logger.info("Instantiating Redis Client")
    try:
        redis_client = redis.Redis(
            host="redis-13803.c124.us-central1-1.gce.cloud.redislabs.com",
            port=13803,
            password=os.getenv("_REDIS_PASSWORD"),
        )
        return redis_client
    except Exception as e:
        custom_logger.error(f"Error with Redis Client: {e}")
        return None


redis_client = get_redis_client()


# authentication
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = "SECRET"

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, minutes=30),
            "iat": datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
