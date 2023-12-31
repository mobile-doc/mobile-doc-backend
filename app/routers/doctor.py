from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
import json
from ..util import get_db, custom_logger, AuthHandler
from ..app_models.doctor import Doctor, DoctorOutput, DoctorUpdateInput
from ..app_models.EHR import Session

router = APIRouter()

auth_handler = AuthHandler()


@router.post(
    "/doctor/new",
    tags=["Doctor"],
    summary="Creates a new doctor",
)
async def create_doctor(doctor_details: Doctor):
    custom_logger.info("create_doctor endpoint called")
    # checking if doctor_id already exists.
    db = get_db()
    db_result_1 = db.patient.find_one({"patient_id": doctor_details.doctor_id})
    db_result_2 = db.doctor.find_one({"doctor_id": doctor_details.doctor_id})

    if db_result_1 or db_result_2:
        return {"success": False, "message": "doctor_id exists. Try another one"}
    else:
        doctor_details.password = auth_handler.get_password_hash(
            doctor_details.password
        )

        insert_result = db.doctor.insert_one(jsonable_encoder(doctor_details))

        if insert_result:
            return {
                "success": True,
                "insert_id": str(insert_result.inserted_id),
                "inserted_doctor": doctor_details,
                "message": "doctor was inserted successfully",
            }
        else:
            return {
                "success": False,
                "message": "doctor could not be inserted. potential db issue",
            }


@router.get(
    "/doctor/{doctor_id}",
    tags=["Doctor"],
    summary="Returns profile of a doctor for a valid doctor_id",
)
async def get_doctor(doctor_id: str):
    custom_logger.info(f"get_doctor endpoint called for doctor_id={doctor_id}")
    db = get_db()

    db_result = db.doctor.find_one(
        filter={"doctor_id": doctor_id}, projection={"_id": False}
    )

    if db_result is None:
        return {
            "success": False,
            "message": f"Doctor_id='{doctor_id}' doesn't exists",
        }

    validated_result = DoctorOutput.parse_raw(json.dumps(db_result, default=str))

    if db_result == None:
        custom_logger.info(f"doctor id='{doctor_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"doctor id='{doctor_id}' not found"
        )

    return {
        "success": True,
        "doctor": validated_result,
    }


@router.put(
    "/doctor/{doctor_id}",
    tags=["Doctor"],
    summary="Updates profile of a doctor for a valid doctor_id",
)
async def update_doctor(
    doctor_id: str,
    doctor_details: DoctorUpdateInput,
    auth_id=Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"update_doctor endpoint called for doctor_id={doctor_id}")
    if doctor_id != auth_id:
        custom_logger.error(f"{auth_id} is trying to perform action of {doctor_id}")
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db = get_db()

    update_result = db.doctor.update_one(
        {"doctor_id": doctor_id}, {"$set": jsonable_encoder(doctor_details)}
    )

    if update_result.modified_count == 1:
        return {
            "success": True,
            "message": f"doctor_id='{doctor_id}' was updated successfully",
        }
    else:
        return {
            "success": False,
            "message": f"doctor_id='{doctor_id}' was not updated. potential db issue",
        }


@router.get(
    "/doctor/{doctor_id}/all_sessions",
    tags=["Doctor"],
    summary="Returns all the sessions of a doctor given a valid doctor ID",
)
async def get_sessions(doctor_id: str, auth_id=Depends(auth_handler.auth_wrapper)):
    custom_logger.info(f"get_sessions endpoint called for doctor_id='{doctor_id}'")
    if doctor_id != auth_id:
        custom_logger.error(f"{auth_id} is trying to perform action of {doctor_id}")
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db = get_db()
    db_result = db.doctor.find_one({"doctor_id": doctor_id})

    if db_result == None:
        custom_logger.info(f"doctor_id='{doctor_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"doctor id='{doctor_id}' not found"
        )

    db_result = db.session.find({"doctor_id": doctor_id})

    doctor_sessions = [Session.parse_raw(json.dumps(x, default=str)) for x in db_result]

    doctor_sessions = [x.dict() for x in doctor_sessions]

    for doctor_session in doctor_sessions:
        db_result = db.patient.find_one(
            filter={"patient_id": doctor_session["patient_id"]}, projection={"name": 1}
        )
        patient_name = db_result["name"] if db_result else None
        doctor_session["patient_name"] = patient_name
    return {
        "success": True,
        "doctor_sessions": doctor_sessions,
    }
