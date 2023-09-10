from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from ..app_models.EHR import Session, SymptomEntry, Prescription, UpdateSessionTimeInput
from ..app_models.doctor import SessionDetails
from ..app_models.notification import Notification
import uuid
from ..util import get_db, custom_logger, AuthHandler

router = APIRouter()
auth_handler = AuthHandler()


@router.get(
    "/session/new/{patient_id}",
    tags=["Session-Patient-Doctor"],
    summary="Creates a new session between doctor and patient",
)
async def create_session(
    patient_id: str, auth_id: str = Depends(auth_handler.auth_wrapper)
):
    custom_logger.info(f"create_session endpoint called for patient_id='{patient_id}'")
    db = get_db()

    db_result = db.patient.find_one({"patient_id": patient_id})

    if db_result == None:
        custom_logger.error(f"patient {patient_id} does not exist")
        raise HTTPException(
            status_code=404, detail=f"patient_id={patient_id} not found"
        )

    if patient_id != auth_id:
        custom_logger.error(f"{auth_id} is trying to perform action of {patient_id}")
        raise HTTPException(status_code=403, detail="Unauthorized action")

    session_id = uuid.uuid4().hex
    created_session = Session(session_id=session_id, patient_id=patient_id)
    created_session = jsonable_encoder(created_session)

    insert_result = db.session.insert_one(created_session)

    if insert_result.acknowledged:
        notification = Notification(
            message="New session created", session_id=session_id, user_id=patient_id
        )
        notification = jsonable_encoder(notification)
        db.notification.insert_one(notification)
        return {
            "success": True,
            "created_session_id": session_id,
            "message": f"Created a new session for patient_id='{patient_id}'",
        }
    else:
        return {
            "success": False,
            "message": "Could not create a session. Database error",
        }


@router.get(
    "/session/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Get all the details of a session.",
)
async def get_session(
    session_id: str, auth_id: str = Depends(auth_handler.auth_wrapper)
):
    custom_logger.info(f"get_session endpoint called for session_id='{session_id}'")
    db = get_db()
    db_result = db.session.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"session id='{session_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"session id='{session_id}' not found"
        )

    validated_session = Session.parse_obj(db_result)

    if (
        validated_session.patient_id != auth_id
        and validated_session.doctor_id != auth_id
    ):
        custom_logger.error(
            f"{auth_id} is tring to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    return {
        "success": True,
        "message": f"providing session details for session_id='{session_id}'",
        "session": validated_session,
    }


@router.post(
    "/session/symptoms/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Add a new symptom to existing session",
)
async def add_symptoms(
    session_id: str,
    symptom_entry: SymptomEntry,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"add_symptoms endpoint called for session_id='{session_id}'")
    db = get_db()

    db_result = db.session.find_one({"session_id": session_id})

    if db_result == None:
        custom_logger.info(f"session id='{session_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"session id='{session_id}' not found"
        )

    if db_result["patient_id"] != auth_id and db_result["doctor_id"] != auth_id:
        custom_logger.error(
            f"{auth_id} is tring to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    symptom_dict_list = db_result["symptom_list"]
    total_symptom_list = [x["symptom_name"] for x in symptom_dict_list]
    total_symptom_list.append(symptom_entry.symptom_name)

    # update the db
    symptom_entry_json = jsonable_encoder(symptom_entry)

    db_update = db.session.update_one(
        {"session_id": session_id}, {"$push": {"symptom_list": symptom_entry_json}}
    )

    # correlated-symptom list
    correlated_symptoms_set = set()
    for each_added_symptom in total_symptom_list:
        each_correlated_symptoms = db.symptoms.find_one(
            filter={"symptom_name": each_added_symptom},
            projection={"correlated_symptoms": 1, "_id": 0},
        )
        if each_correlated_symptoms is None:
            continue

        correlated_symptoms_set = correlated_symptoms_set.union(
            set(each_correlated_symptoms["correlated_symptoms"])
        )

    correlated_symptoms_set = correlated_symptoms_set.difference(
        set(total_symptom_list)
    )

    if db_update.modified_count == 1:
        return {
            "success": True,
            "message": f"Successfully added symptoms to 'session_id'={session_id} ",
            "symptom_added": symptom_entry,
            "correlated_symptoms": list(correlated_symptoms_set),
        }
    else:
        return {
            "success": False,
            "message": f"Could not add symptoms to 'session_id'={session_id}. Potential DB issue",
        }


@router.get(
    "/session/suggested_doctors/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Suggests a list of doctors based on provided symptoms",
)
async def get_suggested_doctors(
    session_id: str,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(
        f"get_suggested_doctors endpoint called for session_id='{session_id}'"
    )
    db = get_db()

    db_result = db.session.find_one({"session_id": session_id})

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

    symptom_dict_list = db_result["symptom_list"]
    symptom_list = [x["symptom_name"] for x in symptom_dict_list]
    symptom_list = set(symptom_list)

    required_doctor_specialities = set()

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
        {"speciality": {"$in": required_doctor_specialities}}, projection={"_id": 0}
    )

    suggested_doctors = [x for x in db_result]

    return {
        "success": True,
        "required_doctor_specialities": required_doctor_specialities,
        "suggested_doctors": suggested_doctors,
    }


@router.post(
    "/session/update_session_time/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Updates start_time and end_time for a session. ",
)
async def update_session_time(
    session_id: str,
    input_updated_time: UpdateSessionTimeInput,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(
        f"update_session_time endpoint called for session_id='{session_id}'"
    )
    db = get_db()
    db_result = db.session.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"session id='{session_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"session id='{session_id}' not found"
        )

    session_doctor = db_result["doctor_id"]
    old_start_time = db_result["start_time"]
    old_end_time = db_result["end_time"]

    if session_doctor is None:
        return {
            "success": False,
            "message": f"First select a doctor before changing time for session_id='{session_id}'",
        }

    print(db_result)

    if db_result["patient_id"] != auth_id and db_result["doctor_id"] != auth_id:
        custom_logger.error(
            f"{auth_id} is trying to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    start_time = input_updated_time.start_time
    end_time = input_updated_time.end_time

    db_update = db.session.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "start_time": start_time,
                "end_time": end_time,
            }
        },
    )

    # also update the doctor's calendar
    doctor_calendar_pull = db.doctor.update_one(
        {"doctor_id": session_doctor},
        {
            "$pull": {
                "calendar": {
                    "start_time": old_start_time,
                    "end_time": old_end_time,
                    "session_id": session_id,
                }
            }
        },
    )
    doctor_db_update = db.doctor.update_one(
        {"doctor_id": session_doctor},
        {
            "$push": {
                "calendar": SessionDetails(
                    start_time=start_time, end_time=end_time, session_id=session_id
                ).dict()
            }
        },
    )

    if db_update.modified_count == 1 or doctor_db_update.modified_count == 1:
        return {
            "success": True,
            "message": f"Session time was updated for session_id='{session_id}'",
            "input_updated_time": input_updated_time,
        }
    else:
        return {
            "success": False,
            "message": f"No Change was made for session_id='{session_id}'",
        }


@router.post(
    "/session/update_session_doctor/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Updates doctor_id for a session. ",
)
async def update_session_doctor(
    session_id: str,
    input_doctor_id: str,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(
        f"update_session_doctor endpoint called for session_id='{session_id}'"
    )
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

    db_result = db.doctor.find_one(
        filter={"doctor_id": input_doctor_id}, projection={"doctor_id": 1}
    )

    if db_result == None:
        custom_logger.info(f"doctor_id id='{input_doctor_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"doctor_id id='{input_doctor_id}' not found"
        )

    db_update = db.session.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "doctor_id": input_doctor_id,
            }
        },
    )

    if db_update.modified_count == 1:
        return {
            "success": True,
            "message": f"Session doctor was updated for session_id='{session_id}'",
            "input_doctor_id": input_doctor_id,
        }
    else:
        return {
            "success": False,
            "message": f"No Change was made for session_id='{session_id}'",
        }


@router.post(
    "/session/update_video_call_link/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Updates video_call_link for a session. ",
)
async def update_video_call_link(
    session_id: str,
    input_video_call_link: str,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(
        f"update_video_call_link endpoint called for session_id='{session_id}'"
    )
    db = get_db()
    db_result = db.session.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"session id='{session_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"session id='{session_id}' not found"
        )

    if db_result["patient_id"] != auth_id and db_result["doctor_id"] != auth_id:
        custom_logger.error(
            f"{auth_id} is trying to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db_update = db.session.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "video_call_link": input_video_call_link,
            }
        },
    )

    if db_update.modified_count == 1:
        return {
            "success": True,
            "message": f"Session doctor was updated for session_id='{session_id}'",
            "video_call_link": input_video_call_link,
        }
    else:
        return {
            "success": False,
            "message": f"No Change was made for session_id='{session_id}'",
        }


@router.put(
    "/session/update_prescription/{session_id}",
    tags=["Session-Patient-Doctor"],
    summary="Updates prescription for a session. ",
)
async def update_prescription(
    session_id: str,
    input_prescription: Prescription,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(
        f"update_prescription endpoint called for session_id='{session_id}'"
    )
    db = get_db()
    db_result = db.session.find_one(
        filter={"session_id": session_id}, projection={"_id": 0}
    )

    if db_result == None:
        custom_logger.info(f"session id='{session_id}' not found")
        raise HTTPException(
            status_code=404, detail=f"session id='{session_id}' not found"
        )

    if db_result["doctor_id"] != auth_id:
        custom_logger.error(
            f"{auth_id} is trying to perform action on session='{session_id}'"
        )
        raise HTTPException(status_code=403, detail="Unauthorized action")

    db_update = db.session.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "diagnosis": input_prescription.diagnosis,
                "advice": input_prescription.advice,
                "suggested_test_list": input_prescription.suggested_test_list,
                "suggested_medicine_list": input_prescription.suggested_medicine_list,
            }
        },
    )

    if db_update.modified_count == 1:
        return {
            "success": True,
            "message": f"Prescription was updated for session_id='{session_id}'",
            "updated_prescription": input_prescription,
        }
