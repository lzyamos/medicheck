from pydantic import BaseModel
from typing import List, Dict

class MedicalHistoryUpdate(BaseModel):
    items: List[Dict]

class MedicationsUpdate(BaseModel):
    meds: List[Dict]

class DoctorNoteCreate(BaseModel):
    patient_id: str
    note_text: str
