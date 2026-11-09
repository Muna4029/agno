from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class UserMemory:
    """Model for User Memories"""

    memory: str
    topics: list[str] | None = None
    input: str | None = None
    last_updated: datetime | None = None
    memory_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        _dict = {
            "memory_id": self.memory_id,
            "memory": self.memory,
            "topics": self.topics,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "input": self.input,
        }
        return {k: v for k, v in _dict.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserMemory:
        last_updated = data.get("last_updated")
        if last_updated:
            data["last_updated"] = datetime.fromisoformat(last_updated)
        return cls(**data)


@dataclass
class SessionSummary:
    """Model for Session Summary."""

    summary: str
    topics: list[str] | None = None
    last_updated: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        _dict = {
            "summary": self.summary,
            "topics": self.topics,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
        return {k: v for k, v in _dict.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionSummary:
        last_updated = data.get("last_updated")
        if last_updated:
            data["last_updated"] = datetime.fromisoformat(last_updated)
        return cls(**data)
