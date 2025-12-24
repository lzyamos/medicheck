from pydantic import BaseModel, EmailStr, Field
from typing import Literal


# -----------------------------
# Request Schemas
# -----------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["patient", "doctor", "institution"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -----------------------------
# Response Schemas
# -----------------------------

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
