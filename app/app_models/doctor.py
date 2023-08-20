from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime, time


class DailyAvailability(BaseModel):
    day_of_the_week: constr(regex="sat|sun|mon|tue|wed|thu|fri")
    day_start_times: List[time]


class SessionDetails(BaseModel):
    start_time: datetime
    end_time: datetime
    session_id: Optional[str]


class Doctor(BaseModel):
    doctor_id: str
    name: str
    email: str
    password: str
    designation: str
    degrees: str  # list of degrees seperated by comma
    speciality: constr(
        regex="Neurologist|Cardiologist|ENT|Gastroenterologist|Pulmonologist|Medicine|Orthopedist|OBGYN"
    )
    availability: List[DailyAvailability]
    calendar: Optional[List[SessionDetails]] = []

    class Config:
        schema_extra = {
            "example": {
                "doctor_id": "BD100",
                "name": "Dr. Abdul Malik",
                "email": "dr.abdul.malik@example.com",
                "password": "1234",
                "designation": "Senior Consultant",
                "degrees": "MBBS, MD (Internal Medicine), DM (Medicine)",
                "speciality": "Medicine",
                "availability": [
                    {
                        "day_of_the_week": "mon",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                    {
                        "day_of_the_week": "tue",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                    {
                        "day_of_the_week": "wed",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                    {
                        "day_of_the_week": "thu",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                    {
                        "day_of_the_week": "fri",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                    {
                        "day_of_the_week": "sat",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                    {
                        "day_of_the_week": "sun",
                        "day_start_times": ["09:00:00", "09:15:00", "09:30:00"],
                    },
                ],
            }
        }


class DoctorOutput(BaseModel):
    doctor_id: str
    name: str
    email: Optional[str]
    designation: str
    degrees: str
    speciality: str
    availability: Optional[List[DailyAvailability]]
    calendar: Optional[List[SessionDetails]]
