from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from agno.utils.log import logger


@dataclass
class TeamSession:
    """Team Session that is stored in the database"""

    # Session UUID
    session_id: str
    # ID of the team session this team session is associated with (so for sub-teams)
    team_session_id: str | None = None
    # ID of the team that this session is associated with
    team_id: str | None = None
    # ID of the user interacting with this team
    user_id: str | None = None
    # Team Memory
    memory: dict[str, Any] | None = None
    # Team Data: agent_id, name and model
    team_data: dict[str, Any] | None = None
    # Session Data: session_name, session_state, images, videos, audio
    session_data: dict[str, Any] | None = None
    # Extra Data stored with this agent
    extra_data: dict[str, Any] | None = None
    # The unix timestamp when this session was created
    created_at: int | None = None
    # The unix timestamp when this session was last updated
    updated_at: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def telemetry_data(self) -> dict[str, Any]:
        return {
            "model": self.team_data.get("model") if self.team_data else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> TeamSession | None:
        if data is None or data.get("session_id") is None:
            logger.warning("TeamSession is missing session_id")
            return None
        return cls(
            session_id=data.get("session_id"),  # type: ignore
            team_id=data.get("team_id"),
            team_session_id=data.get("team_session_id"),
            user_id=data.get("user_id"),
            memory=data.get("memory"),
            team_data=data.get("team_data"),
            session_data=data.get("session_data"),
            extra_data=data.get("extra_data"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
