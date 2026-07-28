from __future__ import annotations

from typing import Any

from agno.infra.base import InfraBase


class InfraResources(InfraBase):
    """InfraResources is a group of InfraResource and InfraApp objects
    that are managed together.
    """

    apps: list[Any] | None = None
    resources: list[Any] | None = None

    def create_resources(
        self,
        group_filter: str | None = None,
        name_filter: str | None = None,
        type_filter: str | None = None,
        dry_run: bool | None = False,
        auto_confirm: bool | None = False,
        force: bool | None = None,
        pull: bool | None = None,
    ) -> tuple[int, int]:
        raise NotImplementedError

    def delete_resources(
        self,
        group_filter: str | None = None,
        name_filter: str | None = None,
        type_filter: str | None = None,
        dry_run: bool | None = False,
        auto_confirm: bool | None = False,
        force: bool | None = None,
    ) -> tuple[int, int]:
        raise NotImplementedError

    def update_resources(
        self,
        group_filter: str | None = None,
        name_filter: str | None = None,
        type_filter: str | None = None,
        dry_run: bool | None = False,
        auto_confirm: bool | None = False,
        force: bool | None = None,
        pull: bool | None = None,
    ) -> tuple[int, int]:
        raise NotImplementedError

    def save_resources(
        self,
        group_filter: str | None = None,
        name_filter: str | None = None,
        type_filter: str | None = None,
    ) -> tuple[int, int]:
        raise NotImplementedError
