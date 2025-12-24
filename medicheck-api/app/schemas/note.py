from pydantic import BaseModel
from typing import Optional

class NoteCreateIn(BaseModel):
    text: str
    patient_id: Optional[str] = None

class NoteOut(BaseModel):
    id: str
    text: str
    patient_id: Optional[str]
    created_at: str
