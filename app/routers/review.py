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


@router.get(
    "/review/{session_id}",
    tags=["Review"],
    summary="Get review for a session (only for patient))",
)
async def get_review(
    session_id: str,
    auth_id=Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"get_review endpoint called for session_id={session_id}")
    db = get_db()
    db_result = db.review.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"Review for session id='{session_id}' not found")
        raise HTTPException(
            status_code=404,
            detail=f"Review for session id='{session_id}' not found. You can request a review using /review/request/{session_id}",
        )

    session_review = Review.parse_obj(db_result)

    db_result = db.session.find_one(
        filter={"session_id": session_id}, projection={"_id": 0, "patient_id": 1}
    )

    if db_result["patient_id"] != auth_id:
        custom_logger.error(
            f"{auth_id} is trying to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    return {
        "success": True,
        "review": session_review.reviews,
    }


@router.get(
    "/review/doctor/{doctor_id}",
    tags=["Review"],
    summary="Get pending peer reviews for a doctor",
)
async def get_pending_peer_reviews(
    doctor_id: str,
    auth_id=Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(
        f"get_pending_peer_reviews endpoint called for doctor_id={doctor_id}"
    )
    if doctor_id != auth_id:
        custom_logger.error(
            f"{auth_id} is trying to perform action on doctor_id='{doctor_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db = get_db()
    db_result = db.review.find(
        # filter out results where requested_reviewer_ids has doctor_id in it
        filter={"requested_reviewer_ids": {"$in": [doctor_id]}},
        projection={"_id": 0},
    )

    if db_result == None:
        custom_logger.info(f"No pending peer reviews for doctor_id='{doctor_id}'")
        return {
            "success": True,
            "pending_peer_reviews": [],
            "message": f"No pending peer reviews for doctor_id='{doctor_id}'",
        }

    else:
        pending_peer_reviews = [Review.parse_obj(x) for x in db_result]
        return {
            "success": True,
            "pending_peer_reviews": pending_peer_reviews,
            "message": f"Found {len(pending_peer_reviews)} pending peer reviews for doctor_id='{doctor_id}'",
        }


@router.post(
    "/review/submit/{session_id}",
    tags=["Review"],
    summary="Submit a review for a session (only for doctor)",
)
async def submit_review(
    session_id: str,
    review: str,
    auth_id=Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"submit_review endpoint called for session_id={session_id}")
    db = get_db()
    db_result = db.review.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"Review for session id='{session_id}' not found")
        raise HTTPException(
            status_code=404,
            detail=f"Review for session id='{session_id}' not found. You can request a review using /review/request/{session_id}",
        )

    session_review = Review.parse_obj(db_result)

    if auth_id not in session_review.requested_reviewer_ids:
        custom_logger.error(
            f"{auth_id} is trying to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    session_review.requested_reviewer_ids.remove(auth_id)

    session_review.reviews.append({"reviewer_id": auth_id, "review": review})

    session_review = jsonable_encoder(session_review)

    db_update = db.review.update_one(
        filter={"session_id": session_id},
        update={"$set": session_review},
    )

    if db_update.modified_count == 0:
        custom_logger.error(f"review update failed for session_id={session_id}")
        return {
            "success": False,
            "message": f"review update failed for session_id={session_id}",
        }
    else:
        return {
            "success": True,
            "session_id": session_id,
            "message": "Review submitted successfully",
        }
