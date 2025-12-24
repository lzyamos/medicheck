from fastapi import APIRouter, Request, HTTPException
from app.core.auth_dependency import get_current_user
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.message import MessageCreate
from app.services.consent_check import doctor_has_consent

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("")
def send_message(payload: MessageCreate, request: Request, authorization: str = ""):
    user = get_current_user(authorization)

    if user["role"] not in {"PATIENT", "DOCTOR"}:
        raise HTTPException(status_code=403, detail="Messaging not permitted.")

    if user["role"] == "DOCTOR":
        if not doctor_has_consent(user["user_id"], payload.patient_id):
            raise HTTPException(status_code=403, detail="No patient consent.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages(
                  patient_id, sender_user_id, sender_role,
                  receiver_user_id, message_text
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    payload.patient_id,
                    user["user_id"],
                    user["role"],
                    payload.receiver_user_id,
                    payload.message_text,
                )
            )
            row = cur.fetchone()
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="MESSAGE_SENT",
        target_type="PATIENT",
        target_id=payload.patient_id,
        metadata_json={"receiver": payload.receiver_user_id},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"ok": True, "message_id": row["id"]}


@router.get("/patient/{patient_id}")
def get_conversation(patient_id: str, request: Request, authorization: str = ""):
    user = get_current_user(authorization)

    if user["role"] == "DOCTOR":
        if not doctor_has_consent(user["user_id"], patient_id):
            raise HTTPException(status_code=403, detail="No patient consent.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM messages
                WHERE patient_id=%s
                  AND (sender_user_id=%s OR receiver_user_id=%s)
                ORDER BY created_at ASC
                """,
                (patient_id, user["user_id"], user["user_id"])
            )
            rows = cur.fetchall()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="MESSAGE_THREAD_VIEWED",
        target_type="PATIENT",
        target_id=patient_id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"messages": rows}
