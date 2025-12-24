from fastapi import APIRouter, Request, HTTPException
from app.core.auth_dependency import get_current_user
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.patient_records import DoctorNoteCreate
from app.services.consent_check import doctor_has_consent

router = APIRouter(prefix="/doctor-notes", tags=["doctor-notes"])

@router.post("")
def create_doctor_note(payload: DoctorNoteCreate, request: Request, authorization: str = ""):
    user = get_current_user(authorization)

    if user["role"] != "DOCTOR":
        raise HTTPException(status_code=403, detail="Only doctors may create notes.")

    if not doctor_has_consent(user["user_id"], payload.patient_id):
        raise HTTPException(status_code=403, detail="No patient consent.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO doctor_notes(patient_id, doctor_user_id, note_text)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (payload.patient_id, user["user_id"], payload.note_text)
            )
            row = cur.fetchone()
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="DOCTOR_NOTE_CREATED",
        target_type="PATIENT",
        target_id=payload.patient_id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"ok": True, "note_id": row["id"]}
