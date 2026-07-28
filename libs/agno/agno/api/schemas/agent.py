from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AgentSessionCreate(BaseModel):
    """Data sent to API to create an Agent Session"""

    session_id: str
    agent_data: dict[str, Any] | None = None


class AgentRunCreate(BaseModel):
    """Data sent to API to create an Agent Run"""

    session_id: str
    team_session_id: str | None = None
    run_id: str | None = None
    run_data: dict[str, Any] | None = None
    agent_data: dict[str, Any] | None = None


class AgentCreate(BaseModel):
    """Data sent to API to create an Agent"""

    agent_id: str
    team_id: str | None = None
    app_id: str | None = None
    workflow_id: str | None = None
    name: str | None = None
    config: dict[str, Any]
