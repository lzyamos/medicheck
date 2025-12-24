from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from app.core.db import get_conn

TRIAGE_RANK = {
    "emergency": 4,
    "urgent": 3,
    "routine": 2,
    "self_care": 1,
    "unknown": 0,
}


def _get_fact(context: Dict[str, Any], fact: str) -> Any:
    """
    Supports:
      - "symptom" -> handled specially by op 'has'
      - "age", "duration_hours", "pregnant", "sex"
      - "vitals.temp_c" style nested access
      - "extras.some_key" style nested access
    """
    if fact in context:
        return context.get(fact)
    parts = fact.split(".")
    cur: Any = context
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def _compare(op: str, left: Any, right: Any, *, symptoms_set: set[str]) -> bool:
    """
    Operations supported:
      - has: fact must be "symptom", right is symptom key string
      - ==, !=, >, >=, <, <=
      - in: right is list, left must be element
      - contains: left is list/str, right must be in left
      - exists: checks left is not None
    """
    if op == "has":
        if right is None:
            return False
        return str(right) in symptoms_set

    if op == "exists":
        return left is not None

    if left is None:
        return False

    if op == "==":
        return left == right
    if op == "!=":
        return left != right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == "in":
        if not isinstance(right, (list, tuple, set)):
            return False
        return left in right
    if op == "contains":
        if isinstance(left, (list, tuple, set)):
            return right in left
        if isinstance(left, str):
            return str(right) in left
        return False

    return False


def _eval_clause(clause: Dict[str, Any], context: Dict[str, Any], symptoms_set: set[str]) -> bool:
    fact = clause.get("fact")
    op = clause.get("op")
    value = clause.get("value")

    if not fact or not op:
        return False

    left = _get_fact(context, fact)
    return _compare(op, left, value, symptoms_set=symptoms_set)


def _eval_conditions(conditions: Dict[str, Any], context: Dict[str, Any], symptoms_set: set[str]) -> bool:
    """
    Expected structure:
      {
        "all": [ {fact,op,value}, ... ],
        "any": [ ... ],
        "none": [ ... ]
      }
    Rules:
      - "all" must all be True (if present)
      - "any" must have at least one True (if present)
      - "none" must all be False (if present)
    """
    all_list = conditions.get("all", [])
    any_list = conditions.get("any", [])
    none_list = conditions.get("none", [])

    if all_list:
        for c in all_list:
            if not _eval_clause(c, context, symptoms_set):
                return False

    if any_list:
        ok = any(_eval_clause(c, context, symptoms_set) for c in any_list)
        if not ok:
            return False

    if none_list:
        for c in none_list:
            if _eval_clause(c, context, symptoms_set):
                return False

    return True


def _pick_best_triage(triage_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not triage_list:
        return {"level": "unknown", "reason": "No matching triage rules."}
    best = triage_list[0]
    best_rank = TRIAGE_RANK.get(str(best.get("level", "unknown")), 0)

    for t in triage_list[1:]:
        rank = TRIAGE_RANK.get(str(t.get("level", "unknown")), 0)
        if rank > best_rank:
            best = t
            best_rank = rank

    return best


def evaluate_rules(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    payload:
      {
        "symptoms": [...],
        "age": ...,
        "duration_hours": ...,
        "pregnant": ...,
        "sex": ...,
        "vitals": {...},
        "extras": {...}
      }
    Returns:
      {
        "triage": {...},
        "recommendations": [...],
        "matched_rules": [...]
      }
    """
    symptoms = payload.get("symptoms") or []
    symptoms_set = {str(s).strip() for s in symptoms if str(s).strip()}

    context = {
        "age": payload.get("age"),
        "duration_hours": payload.get("duration_hours"),
        "pregnant": payload.get("pregnant"),
        "sex": payload.get("sex"),
        "vitals": payload.get("vitals") or {},
        "extras": payload.get("extras") or {},
        # NOTE:
    }

    matched_rules: List[Dict[str, Any]] = []
    triage_candidates: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, module_id, name, severity, priority, conditions, outcomes
                FROM medicheck.rules
                WHERE status = 'active'
                ORDER BY priority ASC, id ASC
                """
            )
            rows = cur.fetchall()

    for r in rows:
        rule_id = r["id"] if isinstance(r, dict) else r[0]
        module_id = r["module_id"] if isinstance(r, dict) else r[1]
        name = r["name"] if isinstance(r, dict) else r[2]
        severity = r["severity"] if isinstance(r, dict) else r[3]
        priority = r["priority"] if isinstance(r, dict) else r[4]
        conditions = r["conditions"] if isinstance(r, dict) else r[5]
        outcomes = r["outcomes"] if isinstance(r, dict) else r[6]

        if not isinstance(conditions, dict) or not isinstance(outcomes, dict):
            continue

        if _eval_conditions(conditions, context, symptoms_set):
            matched_rules.append(
                {
                    "rule_id": int(rule_id),
                    "module_id": int(module_id) if module_id is not None else None,
                    "name": str(name),
                    "severity": str(severity),
                    "priority": int(priority),
                    "outcomes": outcomes,
                }
            )

            triage = outcomes.get("triage")
            if isinstance(triage, dict) and triage.get("level"):
                triage_candidates.append(triage)

            recs = outcomes.get("recommendations")
            if isinstance(recs, list):
                for rec in recs:
                    if isinstance(rec, dict):
                        recommendations.append(rec)
    best_triage = _pick_best_triage(triage_candidates)

    return {
        "triage": best_triage,
        "recommendations": recommendations,
        "matched_rules": matched_rules,
    }
