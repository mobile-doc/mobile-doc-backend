from pydantic import BaseModel, constr
from typing import Optional, List
import uuid


class SymptomEntry(BaseModel):
    symptom_name: str
    duration: Optional[int]
    added_by: constr(regex="doctor|patient")

    class Config:
        schema_extra = {
            "example": {"symptom_name": "fever", "duration": 2, "added_by": "patient"}
        }


class ReviewEntry(BaseModel):
    reviewer_id: str
    review: str

    class Config:
        schema_extra = {
            "example": {
                "reviewer_id": "BD001",
                "review": "The treatment provided was accurate and appropriate",
            }
        }


class Review(BaseModel):
    session_id: str
    diagnosis: Optional[str]
    advice: Optional[str]
    symptom_list: Optional[List[SymptomEntry]] = []
    suggested_test_list: Optional[list[str]] = []
    requested_reviewer_ids: Optional[list[str]] = []
    reviews: Optional[list[ReviewEntry]] = []
