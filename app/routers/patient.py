from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from ..app_models.patient import (
    Patient,
    UpdatePatientInput,
    PatientOutput,
)
from ..app_models.EHR import TestResult, Session
import pickle
import json
from ..util import get_db, custom_logger, redis_client, AuthHandler

auth_handler = AuthHandler()

router = APIRouter()


@router.post(
    "/patient/new",
    tags=["Patient"],
    summary="Creates a new patient",
)
async def create_patient(patient_details: Patient):
    custom_logger.info(f"create_patient endpoint called")
    # checking if patient_id already exists.
    db = get_db()
    db_result_1 = db.patient.find_one({"patient_id": patient_details.patient_id})
    db_result_2 = db.doctor.find_one({"doctor_id": patient_details.patient_id})

    if db_result_1 or db_result_2:
        return {"success": False, "message": "patient_id exists. Try another one"}
    else:
        patient_details.password = auth_handler.get_password_hash(
            patient_details.password
        )

        insert_result = db.patient.insert_one(jsonable_encoder(patient_details))

        if insert_result:
            return {
                "success": True,
                "insert_id": str(insert_result.inserted_id),
                "inserted_patient": patient_details,
                "message": "patient was inserted successfully",
            }
        else:
            return {
                "success": False,
                "message": "patient could not be inserted. potential db issue",
            }


@router.get(
    "/patient/{patient_id}",
    tags=["Patient"],
    summary="Returns details of a patient given authentication",
)
async def get_patient(patient_id: str, auth_id=Depends(auth_handler.auth_wrapper)):
    custom_logger.info(f"get_patient endpoint called for patient_id='{patient_id}'")

    if patient_id != auth_id:
        custom_logger.error(f"{auth_id} is tring to perform action of {patient_id}")
        raise HTTPException(status_code=403, detail="Unauthorized action")

    patient_redis_key = "patient_" + patient_id
    cached_patient = redis_client.get(patient_redis_key)

    if cached_patient:
        custom_logger.info(f"Cache Hit! Found cached data for {patient_redis_key=}")
        patient_details = pickle.loads(cached_patient)

        return {
            "success": True,
            "patient": patient_details,
        }

    else:
        custom_logger.info(f"Cache Miss! {patient_redis_key=}")

        db = get_db()
        db_result = db.patient.find_one({"patient_id": patient_id})

        if db_result == None:
            custom_logger.info(f"Patient id='{patient_id}' not found")
            raise HTTPException(
                status_code=404, detail=f"Patient id='{patient_id}' not found"
            )

        try:
            validated_result = PatientOutput.parse_raw(
                json.dumps(db_result, default=str)
            )
        except:
            custom_logger.error(
                f"Validation error while parsing Patient data for patient_id='{patient_id}'"
            )
            validated_result = None

        # write back to cache
        redis_client.setex(
            name=patient_redis_key,
            value=pickle.dumps(validated_result),
            time=120,
        )
        return {
            "success": True,
            "patient": validated_result,
        }


@router.put(
    "/patient/{patient_id}",
    tags=["Patient"],
    summary="Update details of a patient given authenticated",
)
async def update_patient(
    patient_details: UpdatePatientInput,
    patient_id: str,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"update_patient endpoint called for patient_id='{patient_id}'")
    if patient_id != auth_id:
        custom_logger.error(f"{auth_id} is tring to perform action of {patient_id}")
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db = get_db()
    encoded_patient_details = jsonable_encoder(patient_details)

    update_query = {"$set": encoded_patient_details}

    update_result = db.patient.update_one({"patient_id": patient_id}, update_query)

    if update_result.modified_count == 1:
        return {"success": True, "message": "patient details is updated"}
    else:
        return {"success": False, "message": "patient details could not be updated"}


@router.get(
    "/patient/{patient_id}/all_sessions",
    tags=["Patient"],
    summary="Returns all the sessions of a patient given a valid patient ID",
)
async def get_sessions(patient_id: str, auth_id=Depends(auth_handler.auth_wrapper)):
    custom_logger.info(f"get_sessions endpoint called for patient_id='{patient_id}'")
    if patient_id != auth_id:
        custom_logger.error(f"{auth_id} is tring to perform action of {patient_id}")
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db = get_db()
    db_result = db.patient.find_one({"patient_id": patient_id})

    if db_result == None:
        custom_logger.info(f"Patient id='{patient_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"Patient id='{patient_id}' not found"
        )

    db_result = db.session.find({"patient_id": patient_id})

    patient_sessions = [
        Session.parse_raw(json.dumps(x, default=str)) for x in db_result
    ]

    patient_sessions = [x.dict() for x in patient_sessions]

    for patient_session in patient_sessions:
        db_result = db.doctor.find_one(
            filter={"dcotor_id": patient_session["doctor_id"]}, projection={"name": 1}
        )
        doctor_name = db_result["name"] if db_result else None
        patient_session["doctor_name"] = doctor_name

    return {
        "success": True,
        "patient_sessions": patient_sessions,
    }


@router.get(
    "/patient/EHR/{patient_id}",
    tags=["Patient"],
    summary="Returns the EHR of a patient given a valid patient ID",
)
async def get_EHR(patient_id: str):
    custom_logger.info(f"get_EHR endpoint called for patient_id='{patient_id}'")
    db = get_db()

    db_result = db.patient.find_one({"patient_id": patient_id})

    if db_result == None:
        custom_logger.info(f"Patient id='{patient_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"Patient id='{patient_id}' not found"
        )

    patient_details = PatientOutput.parse_raw(json.dumps(db_result, default=str))

    db_result = db.test_result.find({"patient_id": patient_id})

    test_results = [TestResult.parse_raw(json.dumps(x, default=str)) for x in db_result]

    db_result = db.session.find({"patient_id": patient_id})

    patient_sessions = [
        Session.parse_raw(json.dumps(x, default=str)) for x in db_result
    ]

    return {
        "success": True,
        "patient_details": patient_details,
        "test_results": test_results,
        "patient_sessions": patient_sessions,
    }
