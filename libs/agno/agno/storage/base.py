from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from agno.storage.session import Session


class Storage(ABC):
    def __init__(self, mode: Literal["agent", "team", "workflow"] | None = "agent"):
        self._mode: Literal["agent", "team", "workflow"] = "agent" if mode is None else mode

    @property
    def mode(self) -> Literal["agent", "team", "workflow"]:
        """Get the mode of the storage."""
        return self._mode

    @mode.setter
    def mode(self, value: Literal["agent", "team", "workflow"] | None) -> None:
        """Set the mode of the storage."""
        self._mode = "agent" if value is None else value

    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self, session_id: str, user_id: str | None = None) -> Session | None:
        raise NotImplementedError

    @abstractmethod
    def get_all_session_ids(self, user_id: str | None = None, agent_id: str | None = None) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_all_sessions(self, user_id: str | None = None, entity_id: str | None = None) -> list[Session]:
        raise NotImplementedError

    @abstractmethod
    def get_recent_sessions(
        self,
        user_id: str | None = None,
        entity_id: str | None = None,
        limit: int | None = 2,
    ) -> list[Session]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, session: Session) -> Session | None:
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, session_id: str | None = None):
        raise NotImplementedError

    @abstractmethod
    def drop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def upgrade_schema(self) -> None:
        raise NotImplementedError
