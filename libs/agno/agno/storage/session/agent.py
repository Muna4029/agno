from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from agno.utils.log import logger


@dataclass
class AgentSession:
    """Agent Session that is stored in the database"""

    # Session UUID
    session_id: str
    # ID of the user interacting with this agent
    user_id: str | None = None
    # ID of the team session this agent session is associated with
    team_session_id: str | None = None
    # Agent Memory
    memory: dict[str, Any] | None = None
    # Session Data: session_name, session_state, images, videos, audio
    session_data: dict[str, Any] | None = None
    # Extra Data stored with this agent
    extra_data: dict[str, Any] | None = None
    # The unix timestamp when this session was created
    created_at: int | None = None
    # The unix timestamp when this session was last updated
    updated_at: int | None = None

    # ID of the agent that this session is associated with
    agent_id: str | None = None
    # Agent Data: agent_id, name and model
    agent_data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def telemetry_data(self) -> dict[str, Any]:
        return {
            "model": self.agent_data.get("model") if self.agent_data else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AgentSession | None:
        if data is None or data.get("session_id") is None:
            logger.warning("AgentSession is missing session_id")
            return None
        return cls(
            session_id=data.get("session_id"),  # type: ignore
            agent_id=data.get("agent_id"),
            team_session_id=data.get("team_session_id"),
            user_id=data.get("user_id"),
            memory=data.get("memory"),
            agent_data=data.get("agent_data"),
            session_data=data.get("session_data"),
            extra_data=data.get("extra_data"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
