from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal


TriageLevel = Literal["emergency", "urgent", "routine", "self_care", "unknown"]


class EvaluateRulesRequest(BaseModel):
    symptoms: List[str] = Field(default_factory=list)

    age: Optional[int] = None
    sex: Optional[Literal["male", "female", "other"]] = None
    pregnant: Optional[bool] = None
    duration_hours: Optional[float] = None

    vitals: Dict[str, Any] = Field(default_factory=dict)
    extras: Dict[str, Any] = Field(default_factory=dict)


class MatchedRule(BaseModel):
    rule_id: int
    name: str
    severity: str
    priority: int
    module_id: Optional[int] = None
    outcomes: Dict[str, Any]


class EvaluateRulesResponse(BaseModel):
    triage: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    matched_rules: List[MatchedRule] = Field(default_factory=list)
