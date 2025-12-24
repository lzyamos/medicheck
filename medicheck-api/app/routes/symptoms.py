from fastapi import APIRouter, Request, HTTPException
from app.core.auth_dependency import get_current_user
from app.core.rbac import require_role
from app.core.db import get_conn
from app.core.audit import write_audit_event
from app.schemas.symptom import SymptomSessionCreateIn
from app.services.clinical_rules import evaluate_urgency, condition_insights, recommended_tests
from app.services.consent_check import doctor_has_consent

router = APIRouter(prefix="/symptoms", tags=["symptoms"])

def _patient_id_for_user(user_id: str) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM patients WHERE user_id=%s", (user_id,))
            r = cur.fetchone()
            return str(r["id"]) if r else ""

@router.post("")
def create_symptom_session(payload: SymptomSessionCreateIn, request: Request, authorization: str = ""):
    user = get_current_user(authorization)

    if user["role"] == "PATIENT":
        patient_id = _patient_id_for_user(user["user_id"])
    elif user["role"] == "DOCTOR":
        if not payload.patient_id:
            raise HTTPException(status_code=400, detail="patient_id required for doctor entry.")
        if not doctor_has_consent(user["user_id"], payload.patient_id):
            raise HTTPException(status_code=403, detail="No patient consent.")
        patient_id = payload.patient_id
    else:
        raise HTTPException(status_code=403, detail="Institutions cannot enter symptoms.")

    urgency = evaluate_urgency([s.model_dump() for s in payload.symptoms])
    insights = condition_insights([s.model_dump() for s in payload.symptoms])
    tests = recommended_tests([s.model_dump() for s in payload.symptoms])

    safety_statement = (
        "This output provides assistive clinical guidance only. "
        "It is not a diagnosis and must be reviewed by a licensed medical professional."
    )

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO symptom_sessions(patient_id, created_by_user_id, role_context, answers_json)
                VALUES (%s, %s, %s, %s::jsonb)
                RETURNING id
                """,
                (patient_id, user["user_id"], user["role"], payload.model_dump_json())
            )
            srow = cur.fetchone()
            session_id = str(srow["id"])

            cur.execute(
                """
                INSERT INTO analysis_outputs(
                  symptom_session_id, insights_json, recommended_tests_json,
                  urgency, safety_statement, model_version
                )
                VALUES (%s, %s::jsonb, %s::jsonb, %s, %s, %s)
                RETURNING id
                """,
                (session_id, insights, tests, urgency, safety_statement, "rules-v1")
            )
            arow = cur.fetchone()
        conn.commit()

    write_audit_event(
        actor_user_id=user["user_id"],
        actor_role=user["role"],
        action="SYMPTOM_ANALYSIS_CREATED",
        target_type="SYMPTOM_SESSION",
        target_id=session_id,
        metadata_json={"urgency": urgency},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {
        "session_id": session_id,
        "urgency": urgency,
        "insights": insights,
        "recommended_tests": tests,
        "safety_statement": safety_statement,
    }
