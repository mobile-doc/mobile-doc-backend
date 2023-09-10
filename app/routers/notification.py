from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from ..app_models.notification import Notification
from ..util import get_db, custom_logger, AuthHandler

auth_handler = AuthHandler()

router = APIRouter()


@router.get(
    "/notification",
    tags=["Notification"],
    summary="Returns all notifications for a patient/doctor",
)
async def get_notifications(auth_id=Depends(auth_handler.auth_wrapper)):
    custom_logger.info(f"get_notifications endpoint called for user_id='{auth_id}'")
    db = get_db()
    db_result = db.notification.find(
        {"user_id": auth_id}, projection={"_id": 0}, sort=[("timestamp", -1)]
    )

    all_notifications = [Notification.parse_obj(x) for x in db_result]

    return {
        "success": False,
        "notifications": all_notifications,
    }


@router.post(
    "/notification/seen/{notification_id}",
    tags=["Notification"],
    summary="Mark a notification as seen",
)
async def mark_notification_as_seen(
    notification_id: str, auth_id=Depends(auth_handler.auth_wrapper)
):
    custom_logger.info(
        f"mark_notification_as_seen endpoint called for user_id='{auth_id}, notification_id='{notification_id}'"
    )

    if auth_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = get_db()
    db_result = db.notification.update_one(
        {"notification_id": notification_id, "user_id": auth_id},
        {"$set": {"is_seen": True}},
    )

    if db_result.modified_count == 1:
        return {"success": True, "message": "Notification marked as seen successfully"}
    else:
        raise HTTPException(status_code=404, detail="Notification not found")
