from fastapi import APIRouter

router = APIRouter(prefix="/session", tags=["session"])

@router.get("/init")
def session_init():
    return {
        "message": "Select your role to continue:",
        "roles": ["PATIENT", "DOCTOR", "INSTITUTION"],
        "rule": "No interaction beyond this prompt is permitted until a role is selected and authenticated."
    }
