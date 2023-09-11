from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime, time
from fastapi.encoders import jsonable_encoder
import os


import pymongo

# atlas_password = os.getenv("_ATLAS_USERNAME")
# atlas_username = os.getenv("_ATLAS_PASSWORD")

atlas_password = "1234"
atlas_username = "user"

client = pymongo.MongoClient(
    f"mongodb+srv://{atlas_username}:{atlas_password}@cluster0.ds5ggbq.mongodb.net/?retryWrites=true&w=majority"
)

db = client.get_database("main_db")


# delete every session where doctor_id is null
db_result = db.session.delete_many({"doctor_id": None})
