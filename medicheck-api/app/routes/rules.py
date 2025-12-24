from fastapi import APIRouter
from app.schemas.rules import EvaluateRulesRequest, EvaluateRulesResponse
from app.services.rules_engine import evaluate_rules

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/evaluate", response_model=EvaluateRulesResponse)
def evaluate(payload: EvaluateRulesRequest):
    result = evaluate_rules(payload.model_dump())
    return result
