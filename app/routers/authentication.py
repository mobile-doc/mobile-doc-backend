from ..util import AuthHandler, get_db
from fastapi import APIRouter, HTTPException, Depends
from ..app_models.authentication import LoginInput

auth_handler = AuthHandler()

router = APIRouter()


@router.post(
    "/login",
    tags=["Authentication"],
    summary="Create access and refresh tokens for user",
)
async def login(login_input: LoginInput):
    db = get_db()
    patient_db_reult = db.patient.find_one({"patient_id": login_input.id})

    if patient_db_reult:
        hashed_pass = patient_db_reult["password"]
        if auth_handler.verify_password(login_input.password, hashed_pass):
            token = auth_handler.encode_token(login_input.id)
            return {"token": token, "type": "patient"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password",
            )

    doctor_db_result = db.doctor.find_one({"doctor_id": login_input.id})
    if doctor_db_result:
        hashed_pass = doctor_db_result["password"]
        if auth_handler.verify_password(login_input.password, hashed_pass):
            token = auth_handler.encode_token(login_input.id)
            return {"token": token, "type": "doctor"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password",
            )

    raise HTTPException(
        status_code=400,
        detail="Incorrect email or password",
    )
