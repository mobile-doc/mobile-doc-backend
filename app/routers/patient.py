from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from ..app_models.patient import Patient, PatientInput
from ..app_models.EHR import TestResult
import pickle
import json
from ..util import get_db, custon_logger, redis_client

router = APIRouter()


@router.get(
    "/patient/{patient_id}",
    tags=["Patient"],
    summary="Returns details of a patient given a valid patient ID",
)
async def get_patient(patient_id: str):
    custon_logger.info(f"get_patient endpoint called for patient_id='{patient_id}'")

    patient_redis_key = "patient_" + patient_id
    cached_patient = redis_client.get(patient_redis_key)

    if cached_patient:
        custon_logger.info(f"Cache Hit! Found cached data for {patient_redis_key=}")
        patient_details = pickle.loads(cached_patient)

        return {
            "success": True,
            "patient": patient_details,
        }

    else:
        custon_logger.info(f"Cache Miss! {patient_redis_key=}")

        db = get_db()
        db_reult = db.patient.find_one({"patient_id": patient_id})

        if db_reult == None:
            custon_logger.info(f"Patient id='{patient_id}' not found")
            raise HTTPException(
                status_code=404, detail=f"Patient id='{patient_id}' not found"
            )

        try:
            validated_result = Patient.parse_raw(json.dumps(db_reult, default=str))
        except:
            custon_logger.error(
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
    summary="Update details of a patient given a valid patient ID",
)
async def get_patient(patient_id: str, patient_details: PatientInput):
    custon_logger.info(f"update_patient endpoint called for patient_id='{patient_id}'")
    db = get_db()
    db_reult = db.patient.find_one({"patient_id": patient_id})

    if db_reult == None:
        custon_logger.info(f"Patient id='{patient_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"Patient id='{patient_id}' not found"
        )

    encoded_patient_details = jsonable_encoder(patient_details)
    encoded_patient_details["patient_id"] = patient_id
    update_result = db.patient.replace_one(
        {"patient_id": patient_id}, encoded_patient_details
    )

    if update_result.modified_count == 1:
        return {"success": True, "message": "patient details is updated"}
    else:
        return {"success": False, "message": "patient details could not be updated"}


@router.get(
    "/patient/EHR/{patient_id}",
    tags=["Patient"],
    summary="Returns the EHR of a patient given a valid patient ID",
)
async def get_EHR(patient_id: str):
    custon_logger.info(f"get_EHR endpoint called for patient_id='{patient_id}'")
    db = get_db()

    db_reult = db.patient.find_one({"patient_id": patient_id})

    if db_reult == None:
        custon_logger.info(f"Patient id='{patient_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"Patient id='{patient_id}' not found"
        )

    patient_details = Patient.parse_raw(json.dumps(db_reult, default=str))

    db_reult = db.test_result.find({"patient_id": patient_id})

    test_results = [TestResult.parse_raw(json.dumps(x, default=str)) for x in db_reult]

    return {
        "success": True,
        "patient_details": patient_details,
        "test_results": test_results,
    }
