from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime


class Medicine(BaseModel):
    name: str
    generic_name: str
    precautions: Optional[list[str]]


class CorrelatedSymptoms(BaseModel):
    symptom_name: str
    correlated_symptoms: list[str]
    required_doctor_speciality: list[str]


class SymptomEntry(BaseModel):
    symptom_name: str
    duration: Optional[int]
    added_by: constr(regex="doctor|patient")

    class Config:
        schema_extra = {
            "example": {"symptom_name": "fever", "duration": 2, "added_by": "patient"}
        }


class Session(BaseModel):
    session_id: str
    patient_id: str
    doctor_id: Optional[str]  # Need to create a session before selecting doctor.
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    video_call_link: Optional[str]
    diagnosis: Optional[str]
    advice: Optional[str]
    symptom_list: Optional[List[SymptomEntry]] = []
    suggested_test_list: Optional[list[str]] = []
    suggested_medicine_list: Optional[list[str]] = []


class UpdateSessionTimeInput(BaseModel):
    start_time: datetime
    end_time: datetime

    class Config:
        schema_extra = {
            "example": {
                "start_time": "2023-08-07 09:00",
                "end_time": "2023-08-07 10:30",
            }
        }


class Prescription(BaseModel):
    diagnosis: str
    advice: str
    suggested_test_list: list[str]
    suggested_medicine_list: list[str]

    class Config:
        schema_extra = {
            "example": {
                "diagnosis": "Seasonal Viral Fever",
                "advice": "Take rest for 2 days.",
                "suggested_test_list": ["CBC test", "Chest X-ray"],
                "suggested_medicine_list": ["Napa", "Seclo"],
            }
        }


class TestDataEntry(BaseModel):
    data_element: str
    data_value: float
    data_unit: str


class TestFileEntry(BaseModel):
    file_name: str
    file_url: str


class TestResult(BaseModel):
    test_name: str
    test_center: Optional[str]
    date: datetime
    numeric_results: Optional[list[TestDataEntry]]
    test_files: Optional[list[TestFileEntry]]


class TestResultInput(BaseModel):
    schema_name: Optional[str]
    test_result: TestResult
    api_key: str

    class Config:
        schema_extra = {
            "example": {
                "schema_name": "CBC",
                "test_result": {
                    "test_name": "CBC (Complete Blood Count)",
                    "test_center": "Ibn Sina Diagonistics Center",
                    "date": "2023-08-21T00:00:00",
                    "numeric_results": [
                        {
                            "data_element": "WBC",
                            "data_value": 5.0,
                            "data_unit": "x10^9/L",
                        },
                        {
                            "data_element": "RBC",
                            "data_value": 4.5,
                            "data_unit": "x10^12/L",
                        },
                        {
                            "data_element": "Hemoglobin",
                            "data_value": 14.0,
                            "data_unit": "g/dL",
                        },
                        {
                            "data_element": "Hematocrit",
                            "data_value": 42.0,
                            "data_unit": "%",
                        },
                        {
                            "data_element": "Platelets",
                            "data_value": 150.0,
                            "data_unit": "x10^9/L",
                        },
                    ],
                    "test_files": [],
                },
                "api_key": "your_api_key_here",
            }
        }
