from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class MemoryRetrieval(str, Enum):
    last_n = "last_n"
    first_n = "first_n"
    semantic = "semantic"


class Memory(BaseModel):
    """Model for Agent Memories"""

    memory: str
    id: str | None = None
    topic: str | None = None
    input: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)
