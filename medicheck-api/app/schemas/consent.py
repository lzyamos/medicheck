from pydantic import BaseModel
from typing import Literal, Optional

GranteeType = Literal["DOCTOR", "INSTITUTION"]

class ConsentGrantIn(BaseModel):
    grantee_type: GranteeType
    grantee_id: str
    scope_json: dict = {}

class ConsentRevokeIn(BaseModel):
    consent_id: str
