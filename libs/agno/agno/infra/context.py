from __future__ import annotations

from pydantic import BaseModel

from agno.api.schemas.workspace import WorkspaceSchema


class ContainerContext(BaseModel):
    """ContainerContext is a context object passed when creating containers."""

    # Workspace name
    workspace_name: str
    # Workspace schema from the API
    workspace_schema: WorkspaceSchema | None = None
    # Path to the workspace directory inside the container
    workspace_root: str
    # Path to the workspace parent directory inside the container
    workspace_parent: str
    # Path to the requirements.txt file relative to the workspace_root
    requirements_file: str | None = None
