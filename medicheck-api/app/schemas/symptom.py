from pydantic import BaseModel
from typing import List, Optional

class SymptomIn(BaseModel):
    symptom: str
    severity: int
    duration_days: int
    progression: Optional[str] = None

class SymptomSessionCreateIn(BaseModel):
    patient_id: Optional[str] = None
    symptoms: List[SymptomIn]
    additional_notes: Optional[str] = None

class AnalysisOut(BaseModel):
    insights: list
    recommended_tests: list
    urgency: str
    safety_statement: str
