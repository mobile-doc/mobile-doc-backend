from pydantic import BaseModel, constr
from datetime import datetime
import uuid


class Notification(BaseModel):
    notification_id: str = uuid.uuid4().hex
    timestamp: datetime = datetime.now()
    message: str
    is_seen: bool = False
    session_id: str
    user_id: str
