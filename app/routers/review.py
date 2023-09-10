from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
import json
from ..util import get_db, custom_logger, AuthHandler
from ..app_models.review import Review
import random

router = APIRouter()

auth_handler = AuthHandler()


@router.post(
    "/review/request/{session_id}",
    tags=["Review"],
    summary="Request a review for a session",
)
async def request_review(
    session_id: str,
    auth_id=Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"request_review endpoint called for session_id={session_id}")
    db = get_db()
    db_result = db.session.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"session id='{session_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"session id='{session_id}' not found"
        )

    if db_result["patient_id"] != auth_id:
        custom_logger.error(
            f"{auth_id} is trying to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    session_doctor = db_result["doctor_id"]
    session_diagnosis = db_result["diagnosis"]
    session_advice = db_result["advice"]
    session_suggested_tests = db_result["suggested_test_list"]
    symptom_dict_list = db_result["symptom_list"]
    symptom_list = [x["symptom_name"] for x in symptom_dict_list]
    symptom_list = set(symptom_list)

    # check for existing review request
    db_result = db.review.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )
    if db_result is not None:
        custom_logger.info(f"review already requested for session_id={session_id}")
        raise HTTPException(
            status_code=400,
            detail=f"review already requested for session_id={session_id}",
        )

    required_doctor_specialities = set()
    required_doctor_specialities.add("Medicine")

    for symptom_name in symptom_list:
        doc_speciality_list = db.symptoms.find_one(
            filter={"symptom_name": symptom_name},
            projection={"_id": 0, "required_doctor_speciality": 1},
        )

        if doc_speciality_list is None:
            continue

        required_doctor_specialities = required_doctor_specialities.union(
            set(doc_speciality_list["required_doctor_speciality"])
        )

    required_doctor_specialities = list(required_doctor_specialities)

    db_result = db.doctor.find(
        {
            "$and": [
                {"speciality": {"$in": required_doctor_specialities}},
                {"doctor_id": {"$ne": session_doctor}},
            ]
        },
        projection={"_id": 0, "doctor_id": 1},
    )

    suggested_reviewers = [x["doctor_id"] for x in db_result]
    random.shuffle(suggested_reviewers)
    suggested_reviewers = suggested_reviewers[:2]

    review = Review(
        session_id=session_id,
        diagnosis=session_diagnosis,
        advice=session_advice,
        symptom_list=symptom_dict_list,
        suggested_test_list=session_suggested_tests,
        requested_reviewer_ids=suggested_reviewers,
    )

    review = jsonable_encoder(review)

    db_insert = db.review.insert_one(review)

    if db_insert.inserted_id is None:
        custom_logger.error(f"review insert failed for session_id={session_id}")
        raise HTTPException(
            status_code=500, detail=f"review insert failed for session_id={session_id}"
        )
    else:
        return {
            "session_id": session_id,
            "message": "Review requested successfully",
        }
