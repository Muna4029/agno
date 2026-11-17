from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    ws_name: str
    git_url: str | None = None
    visibility: str | None = None
    ws_data: dict[str, Any] | None = None


class WorkspaceUpdate(BaseModel):
    id_workspace: str
    ws_name: str | None = None
    git_url: str | None = None
    visibility: str | None = None
    ws_data: dict[str, Any] | None = None
    is_active: bool | None = None


class WorkspaceDelete(BaseModel):
    id_workspace: str
    ws_name: str | None = None


class WorkspaceEvent(BaseModel):
    id_workspace: str
    event_type: str
    event_status: str
    event_data: dict[str, Any] | None = None


class WorkspaceSchema(BaseModel):
    """Workspace data returned by the API."""

    id_workspace: str | None = None
    ws_name: str | None = None
    is_active: bool | None = None
    git_url: str | None = None
    ws_data: dict[str, Any] | None = None


class WorkspaceIdentifier(BaseModel):
    ws_key: str | None = None
    id_workspace: str | None = None
