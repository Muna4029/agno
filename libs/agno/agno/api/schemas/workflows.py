from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WorkflowCreate(BaseModel):
    """Data sent to API to create aWorkflow"""

    workflow_id: str
    app_id: str | None = None
    name: str | None = None
    config: dict[str, Any]
