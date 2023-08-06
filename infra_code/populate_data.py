from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime, time
from fastapi.encoders import jsonable_encoder
import os


class DailyAvailability(BaseModel):
    day_of_the_week: constr(regex="sat|sun|mon|tue|wed|thu|fri")
    day_start_time: time
    day_end_time: time


class SessionDetails(BaseModel):
    session_starttime: datetime
    session_endtime: datetime
    session_id: Optional[str]


class Doctor(BaseModel):
    doctor_id: str
    name: str
    email: str
    password: str
    designation: str
    degrees: str  # list of degrees seperated by comma
    speciality: str
    availability: List[DailyAvailability]
    calendar: List[SessionDetails]


import pymongo

atlas_password = os.getenv("_ATLAS_USERNAME")
atlas_username = os.getenv("_ATLAS_PASSWORD")

client = pymongo.MongoClient(
    f"mongodb+srv://{atlas_username}:{atlas_password}@cluster0.ds5ggbq.mongodb.net/?retryWrites=true&w=majority"
)

db = client.get_database("main_db")


data = {
    "doctor_id": "BD001",
    "name": "Dr. Abdul Malik",
    "email": "dr.abdul.malik@example.com",
    "password": "mypassword",
    "designation": "Senior Consultant",
    "degrees": "MBBS, MD (Internal Medicine), DM (Medicine)",
    "speciality": "Medicine",
    "availability": [
        {
            "day_of_the_week": "mon",
            "day_start_time": "09:00:00",
            "day_end_time": "17:00:00",
        },
        {
            "day_of_the_week": "tue",
            "day_start_time": "09:00:00",
            "day_end_time": "17:00:00",
        },
        {
            "day_of_the_week": "wed",
            "day_start_time": "09:00:00",
            "day_end_time": "17:00:00",
        },
        {
            "day_of_the_week": "thu",
            "day_start_time": "09:00:00",
            "day_end_time": "17:00:00",
        },
        {
            "day_of_the_week": "fri",
            "day_start_time": "09:00:00",
            "day_end_time": "17:00:00",
        },
        {
            "day_of_the_week": "sat",
            "day_start_time": "09:00:00",
            "day_end_time": "13:00:00",
        },
        {
            "day_of_the_week": "sun",
            "day_start_time": "09:00:00",
            "day_end_time": "13:00:00",
        },
    ],
    "calendar": [
        {
            "session_starttime": "2023-08-05T09:00:00",
            "session_endtime": "2023-08-05T12:00:00",
            "session_id": "SESSION001",
        },
        {
            "session_starttime": "2023-08-05T14:00:00",
            "session_endtime": "2023-08-05T17:00:00",
            "session_id": "SESSION002",
        },
    ],
}


dr = Doctor.parse_obj(data)
dr = jsonable_encoder(dr)
db_result = db.doctor.insert_one(dr)
print(db_result.inserted_id)
