from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionSummary(BaseModel):
    """Model for Session Summary."""

    summary: str = Field(
        ...,
        description="Summary of the session. Be concise and focus on only important information. Do not make anything up.",
    )
    topics: list[str] | None = Field(None, description="Topics discussed in the session.")

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True, indent=2)
