from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from agno.workspace.settings import WorkspaceSettings


class InfraBase(BaseModel):
    """Base class for all InfraResource, InfraApp and InfraResources objects."""

    # Name of the infrastructure resource
    name: str | None = None
    # Group for the infrastructure resource
    # Used for filtering infrastructure resources by group
    group: str | None = None
    # Environment filter for this resource
    env: str | None = None
    # Infrastructure filter for this resource
    infra: str | None = None
    # Whether this resource is enabled
    enabled: bool = True

    # Resource Control
    skip_create: bool = False
    skip_read: bool = False
    skip_update: bool = False
    skip_delete: bool = False
    recreate_on_update: bool = False
    # Skip create if resource with the same name is active
    use_cache: bool = True
    # Force create/update/delete even if a resource with the same name is active
    force: bool | None = None

    # Wait for resource to be created, updated or deleted
    wait_for_create: bool = True
    wait_for_update: bool = True
    wait_for_delete: bool = True
    waiter_delay: int = 30
    waiter_max_attempts: int = 50

    # Environment Variables for the resource (if applicable)
    # Add env variables to resource where applicable
    env_vars: dict[str, Any] | None = None
    # Read env from a file in yaml format
    env_file: Path | None = None
    # Add secret variables to resource where applicable
    # secrets_dict: Optional[Dict[str, Any]] = None
    # Read secrets from a file in yaml format
    secrets_file: Path | None = None
    # Read secret variables from AWS Secrets
    aws_secrets: Any | None = None

    # Debug Mode
    debug_mode: bool = False

    # Store resource to output directory
    # If True, save resource output to json files
    save_output: bool = False
    # The directory for the input files in the workspace directory
    input_dir: str | None = None
    # The directory for the output files in the workspace directory
    output_dir: str | None = None

    # Dependencies for the resource
    depends_on: list[Any] | None = None

    # Workspace Settings
    workspace_settings: WorkspaceSettings | None = None

    # Cached Data
    cached_workspace_dir: Path | None = None
    cached_env_file_data: dict[str, Any] | None = None
    cached_secret_file_data: dict[str, Any] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    def get_group_name(self) -> str | None:
        return self.group or self.name

    @property
    def workspace_root(self) -> Path | None:
        return self.workspace_settings.ws_root if self.workspace_settings is not None else None

    @property
    def workspace_name(self) -> str | None:
        return self.workspace_settings.ws_name if self.workspace_settings is not None else None

    @property
    def workspace_dir(self) -> Path | None:
        if self.cached_workspace_dir is not None:
            return self.cached_workspace_dir

        if self.workspace_root is not None:
            from agno.workspace.helpers import get_workspace_dir_path

            workspace_dir = get_workspace_dir_path(self.workspace_root)
            if workspace_dir is not None:
                self.cached_workspace_dir = workspace_dir
                return workspace_dir
        return None

    def set_workspace_settings(self, workspace_settings: WorkspaceSettings | None = None) -> None:
        if workspace_settings is not None:
            self.workspace_settings = workspace_settings

    def get_env_file_data(self) -> dict[str, Any] | None:
        if self.cached_env_file_data is None:
            from agno.utils.yaml_io import read_yaml_file

            self.cached_env_file_data = read_yaml_file(file_path=self.env_file)
        return self.cached_env_file_data

    def get_secret_file_data(self) -> dict[str, Any] | None:
        if self.cached_secret_file_data is None:
            from agno.utils.yaml_io import read_yaml_file

            self.cached_secret_file_data = read_yaml_file(file_path=self.secrets_file)
        return self.cached_secret_file_data

    def get_secret_from_file(self, secret_name: str) -> str | None:
        secret_file_data = self.get_secret_file_data()
        if secret_file_data is not None:
            return secret_file_data.get(secret_name)
        return None

    def get_infra_resources(self) -> Any | None:
        """This method returns an InfraResources object for this resource"""
        raise NotImplementedError("get_infra_resources method not implemented")

    def set_aws_env_vars(self, env_dict: dict[str, str], aws_region: str | None = None) -> None:
        from agno.constants import (
            AWS_DEFAULT_REGION_ENV_VAR,
            AWS_REGION_ENV_VAR,
        )

        if aws_region is not None:
            # logger.debug(f"Setting AWS Region to {aws_region}")
            env_dict[AWS_REGION_ENV_VAR] = aws_region
            env_dict[AWS_DEFAULT_REGION_ENV_VAR] = aws_region
        elif self.workspace_settings is not None and self.workspace_settings.aws_region is not None:
            # logger.debug(f"Setting AWS Region to {aws_region} using workspace_settings")
            env_dict[AWS_REGION_ENV_VAR] = self.workspace_settings.aws_region
            env_dict[AWS_DEFAULT_REGION_ENV_VAR] = self.workspace_settings.aws_region
