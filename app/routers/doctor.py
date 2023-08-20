from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
import json
from ..util import get_db, custom_logger, AuthHandler
from ..app_models.doctor import Doctor, DoctorOutput

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
