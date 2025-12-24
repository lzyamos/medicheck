from typing import Optional
from app.core.db import get_conn

def write_audit_event(
    *,
    actor_user_id: Optional[str],
    actor_role: Optional[str],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata_json: dict | None = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    metadata_json = metadata_json or {}
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit_events(actor_user_id, actor_role, action, target_type, target_id, metadata_json, ip, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                """,
                (actor_user_id, actor_role, action, target_type, target_id, metadata_json, ip, user_agent)
            )
        conn.commit()
