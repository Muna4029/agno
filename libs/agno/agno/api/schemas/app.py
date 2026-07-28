from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AppCreate(BaseModel):
    """Data sent to API to create an App"""

    app_id: str | None = None
    name: str | None = None
    description: str | None = None
    config: dict[str, Any]
