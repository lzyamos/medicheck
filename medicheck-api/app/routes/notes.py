from fastapi import APIRouter, Request
from app.core.auth_dependency import get_current_user
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.note import NoteCreateIn

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("")
def list_notes(request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM notes WHERE owner_user_id=%s ORDER BY created_at DESC", (user["user_id"],))
            rows = cur.fetchall()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="NOTES_LIST",
        metadata_json={},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"items": rows}

@router.post("")
def create_note(payload: NoteCreateIn, request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notes(owner_user_id, patient_id, text)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user["user_id"], payload.patient_id, payload.text)
            )
            row = cur.fetchone()
            note_id = str(row["id"])
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="NOTE_CREATED",
        target_type="NOTE",
        target_id=note_id,
        metadata_json={"patient_id": payload.patient_id},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"ok": True, "note_id": note_id}
