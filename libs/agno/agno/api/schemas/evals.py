from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class EvalType(str, Enum):
    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"


class EvalRunCreate(BaseModel):
    """Data sent to the API to create an evaluation run"""

    agent_id: str | None = None
    model_id: str | None = None
    model_provider: str | None = None
    team_id: str | None = None
    name: str | None = None
    evaluated_entity_name: str | None = None

    run_id: str
    eval_type: EvalType
    eval_data: dict[str, Any]
