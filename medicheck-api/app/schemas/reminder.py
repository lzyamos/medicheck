from pydantic import BaseModel
from typing import Optional

class ReminderCreateIn(BaseModel):
    remind_at: str
    type: str
    payload_json: dict = {}
    patient_id: Optional[str] = None

class ReminderOut(BaseModel):
    id: str
    remind_at: str
    type: str
    status: str
    created_at: str
