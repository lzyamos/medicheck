from fastapi import APIRouter, Request, HTTPException
from app.core.auth_dependency import get_current_user
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.patient_records import MedicalHistoryUpdate, MedicationsUpdate
from app.services.consent_check import can_access_patient

router = APIRouter(prefix="/patients", tags=["patient-records"])

@router.get("/{patient_id}/records")
def get_records(patient_id: str, request: Request, authorization: str = ""):
    user = get_current_user(authorization)

    if not can_access_patient(user, patient_id):
        raise HTTPException(status_code=403, detail="Access denied.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT items_json FROM medical_history WHERE patient_id=%s", (patient_id,))
            history = cur.fetchone()
            cur.execute("SELECT meds_json FROM medications WHERE patient_id=%s", (patient_id,))
            meds = cur.fetchone()
            cur.execute("SELECT * FROM test_results WHERE patient_id=%s ORDER BY collected_at DESC", (patient_id,))
            tests = cur.fetchall()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="PATIENT_RECORDS_VIEWED",
        target_type="PATIENT",
        target_id=patient_id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {
        "medical_history": history["items_json"] if history else [],
        "medications": meds["meds_json"] if meds else [],
        "test_results": tests,
    }

@router.put("/{patient_id}/medical-history")
def update_history(patient_id: str, payload: MedicalHistoryUpdate, request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    if user["role"] != "PATIENT":
        raise HTTPException(status_code=403, detail="Only patients may update history.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO medical_history(patient_id, items_json)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (patient_id)
                DO UPDATE SET items_json=EXCLUDED.items_json, updated_at=now()
                """,
                (patient_id, payload.items)
            )
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="MEDICAL_HISTORY_UPDATED",
        target_type="PATIENT",
        target_id=patient_id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"ok": True}
