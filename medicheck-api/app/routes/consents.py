from fastapi import APIRouter, Request
from app.core.auth_dependency import get_current_user
from app.core.rbac import require_role
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.consent import ConsentGrantIn, ConsentRevokeIn

router = APIRouter(prefix="/consents", tags=["consents"])

def _get_patient_id_for_user(user_id: str) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM patients WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            return str(row["id"]) if row else ""

@router.get("")
def list_consents(request: Request, authorization: str = ""):
    user = get_current_user(authorization)

    with get_conn() as conn:
        with conn.cursor() as cur:
            if user["role"] == "PATIENT":
                patient_id = _get_patient_id_for_user(user["user_id"])
                cur.execute("SELECT * FROM consents WHERE patient_id=%s ORDER BY granted_at DESC", (patient_id,))
            elif user["role"] == "DOCTOR":
                cur.execute("SELECT id FROM doctors WHERE user_id=%s", (user["user_id"],))
                d = cur.fetchone()
                doctor_id = str(d["id"]) if d else ""
                cur.execute(
                    "SELECT * FROM consents WHERE grantee_type='DOCTOR' AND grantee_id=%s AND status='GRANTED'",
                    (doctor_id,)
                )
            else:
                cur.execute("SELECT id FROM institutions WHERE user_id=%s", (user["user_id"],))
                i = cur.fetchone()
                inst_id = str(i["id"]) if i else ""
                cur.execute(
                    "SELECT * FROM consents WHERE grantee_type='INSTITUTION' AND grantee_id=%s AND status='GRANTED'",
                    (inst_id,)
                )
            rows = cur.fetchall()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="CONSENT_LIST",
        metadata_json={},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"items": rows}

@router.post("/grant")
def grant_consent(payload: ConsentGrantIn, request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    require_role(user, {"PATIENT"})

    patient_id = _get_patient_id_for_user(user["user_id"])
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO consents(patient_id, grantee_type, grantee_id, scope_json, status)
                VALUES (%s, %s, %s, %s::jsonb, 'GRANTED')
                RETURNING id
                """,
                (patient_id, payload.grantee_type, payload.grantee_id, payload.scope_json)
            )
            row = cur.fetchone()
            consent_id = str(row["id"])
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="CONSENT_GRANTED",
        target_type="CONSENT",
        target_id=consent_id,
        metadata_json={"grantee_type": payload.grantee_type, "grantee_id": payload.grantee_id},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"ok": True, "consent_id": consent_id}

@router.post("/revoke")
def revoke_consent(payload: ConsentRevokeIn, request: Request, authorization: str = ""):
    user = get_current_user(authorization)
    require_role(user, {"PATIENT"})

    patient_id = _get_patient_id_for_user(user["user_id"])
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE consents
                SET status='REVOKED', revoked_at=now()
                WHERE id=%s AND patient_id=%s
                """,
                (payload.consent_id, patient_id)
            )
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="CONSENT_REVOKED",
        target_type="CONSENT",
        target_id=payload.consent_id,
        metadata_json={},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"ok": True}
