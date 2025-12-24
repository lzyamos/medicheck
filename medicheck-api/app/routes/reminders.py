from fastapi import APIRouter, Request
from app.core.auth_dependency import get_current_user
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.reminder import ReminderCreateIn

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.get("")
def list_reminders(request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM reminders WHERE owner_user_id=%s ORDER BY created_at DESC", (user["user_id"],))
            rows = cur.fetchall()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="REMINDERS_LIST",
        metadata_json={},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"items": rows}

@router.post("")
def create_reminder(payload: ReminderCreateIn, request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reminders(owner_user_id, patient_id, remind_at, type, payload_json)
                VALUES (%s, %s, %s::timestamptz, %s, %s::jsonb)
                RETURNING id
                """,
                (user["user_id"], payload.patient_id, payload.remind_at, payload.type, payload.payload_json)
            )
            row = cur.fetchone()
            reminder_id = str(row["id"])
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="REMINDER_CREATED",
        target_type="REMINDER",
        target_id=reminder_id,
        metadata_json={"patient_id": payload.patient_id, "type": payload.type},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"ok": True, "reminder_id": reminder_id}
