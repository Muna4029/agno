from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaygroundEndpointCreate(BaseModel):
    """Data sent to API to create a playground endpoint"""

    endpoint: str
    playground_data: dict[str, Any] | None = None


class PlaygroundEndpointSchema(BaseModel):
    """Schema for a playground endpoint returned by API"""

    id_workspace: UUID | None = None
    id_playground_endpoint: UUID | None = None
    endpoint: str
    playground_data: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
