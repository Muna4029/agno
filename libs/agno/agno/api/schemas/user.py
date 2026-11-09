from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class UserSchema(BaseModel):
    """Schema for user data returned by the API."""

    id_user: str
    email: str | None = None
    username: str | None = None
    name: str | None = None
    email_verified: bool | None = False
    is_active: bool | None = True
    is_machine: bool | None = False
    user_data: dict[str, Any] | None = None


class EmailPasswordAuthSchema(BaseModel):
    email: str
    password: str
    auth_source: str = "cli"


class TeamSchema(BaseModel):
    """Schema for team data returned by the API."""

    id_team: str
    name: str
    url: str


class TeamIdentifier(BaseModel):
    id_team: str | None = None
    team_url: str | None = None
