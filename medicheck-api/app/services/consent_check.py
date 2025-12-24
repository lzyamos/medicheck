from app.core.db import get_conn

def doctor_has_consent(doctor_user_id: str, patient_id: str) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM doctors WHERE user_id=%s", (doctor_user_id,))
            d = cur.fetchone()
            if not d:
                return False
            doctor_id = str(d["id"])
            cur.execute(
                """
                SELECT 1 FROM consents
                WHERE patient_id=%s
                  AND grantee_type='DOCTOR'
                  AND grantee_id=%s
                  AND status='GRANTED'
                """,
                (patient_id, doctor_id)
            )
            return cur.fetchone() is not None

def can_access_patient(user: dict, patient_id: str) -> bool:
    from app.core.db import get_conn

    if user["role"] == "PATIENT":
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM patients WHERE user_id=%s", (user["user_id"],))
                r = cur.fetchone()
                return r and str(r["id"]) == patient_id

    if user["role"] == "DOCTOR":
        return doctor_has_consent(user["user_id"], patient_id)

    return False
