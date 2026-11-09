from __future__ import annotations

from pathlib import Path

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from agno.api.schemas.workspace import WorkspaceSchema


class WorkspaceSettings(BaseSettings):
    """Workspace settings that can be used by any resource in the workspace."""

    # Workspace name
    ws_name: str
    # Path to the workspace root
    ws_root: Path
    # Workspace git repo url
    ws_repo: str | None = None
    # default env for agno ws commands
    default_env: str | None = "dev"
    # default infra for agno ws commands
    default_infra: str | None = None

    # Image Settings
    # Repository for images
    image_repo: str = "agnohq"
    # 'name:tag' for the image
    image_name: str | None = None
    # If True, build images locally
    build_images: bool = False
    # If True, push images after building
    push_images: bool = False
    # If True, skip cache when building images
    skip_image_cache: bool = False
    # If True, force pull images in FROM
    force_pull_images: bool = False

    # Test Settings
    test_env: str = "test"
    test_key: str | None = None

    # Development Settings
    dev_env: str = "dev"
    dev_key: str | None = None

    # Staging Settings
    stg_env: str = "stg"
    stg_key: str | None = None

    # Production Settings
    prd_env: str = "prd"
    prd_key: str | None = None

    # ag cli settings
    # Set to True if Agno should continue creating
    # resources after a resource creation has failed
    continue_on_create_failure: bool = False
    # Set to True if Agno should continue deleting
    # resources after a resource deleting has failed
    # Defaults to True because we normally want to continue deleting
    continue_on_delete_failure: bool = True
    # Set to True if Agno should continue patching
    # resources after a resource patch has failed
    continue_on_patch_failure: bool = False

    # AWS settings
    # Region for AWS resources
    aws_region: str | None = None
    # Profile for AWS resources
    aws_profile: str | None = None
    # AWS Subnet Ids
    aws_subnet_ids: list[str] = Field(default_factory=list)
    # Public subnets. Will be added to aws_subnet_ids if provided and aws_subnet_ids is empty.
    # Note: not added to aws_subnet_ids if aws_subnet_ids is provided.
    aws_public_subnets: list[str] = Field(default_factory=list)
    # Private subnets. Will be added to aws_subnet_ids if provided and aws_subnet_ids is empty.
    # Note: not added to aws_subnet_ids if aws_subnet_ids is provided.
    aws_private_subnets: list[str] = Field(default_factory=list)
    # AWS Availability Zone
    aws_az1: str | None = None
    aws_az2: str | None = None
    aws_az3: str | None = None
    aws_az4: str | None = None
    aws_az5: str | None = None
    # Security Group Ids
    aws_security_group_ids: list[str] = Field(default_factory=list)

    # Other Settings
    # Use cached resource if available, i.e. skip resource creation if the resource already exists
    use_cache: bool = True
    # WorkspaceSchema provided by the api
    ws_schema: WorkspaceSchema | None = None

    model_config = SettingsConfigDict(extra="allow")

    @field_validator("test_key", mode="before")
    def set_test_key(cls, test_key, info: ValidationInfo):
        if test_key is not None:
            return test_key
        ws_name = info.data.get("ws_name")
        if ws_name is None:
            raise ValueError("`ws_name` is None: Please set a valid value")
        test_env = info.data.get("test_env")
        if test_env is None:
            raise ValueError("`test_env` is None: Please set a valid value")

        return f"{ws_name}-{test_env}"

    @field_validator("dev_key", mode="before")
    def set_dev_key(cls, dev_key, info: ValidationInfo):
        if dev_key is not None:
            return dev_key
        ws_name = info.data.get("ws_name")
        if ws_name is None:
            raise ValueError("`ws_name` is None: Please set a valid value")
        dev_env = info.data.get("dev_env")
        if dev_env is None:
            raise ValueError("`dev_env` is None: Please set a valid value")

        return f"{ws_name}-{dev_env}"

    @field_validator("stg_key", mode="before")
    def set_stg_key(cls, stg_key, info: ValidationInfo):
        if stg_key is not None:
            return stg_key
        ws_name = info.data.get("ws_name")
        if ws_name is None:
            raise ValueError("`ws_name` is None: Please set a valid value")
        stg_env = info.data.get("stg_env")
        if stg_env is None:
            raise ValueError("`stg_env` is None: Please set a valid value")

        return f"{ws_name}-{stg_env}"

    @field_validator("prd_key", mode="before")
    def set_prd_key(cls, prd_key, info: ValidationInfo):
        if prd_key is not None:
            return prd_key
        ws_name = info.data.get("ws_name")
        if ws_name is None:
            raise ValueError("`ws_name` is None: Please set a valid value")
        prd_env = info.data.get("prd_env")
        if prd_env is None:
            raise ValueError("`prd_env` is None: Please set a valid value")

        return f"{ws_name}-{prd_env}"

    @field_validator("aws_subnet_ids", mode="before")
    def set_subnet_ids(cls, aws_subnet_ids, info: ValidationInfo):
        if aws_subnet_ids is not None:
            return aws_subnet_ids

        aws_public_subnets = info.data.get("aws_public_subnets", [])
        aws_private_subnets = info.data.get("aws_private_subnets", [])

        return aws_public_subnets + aws_private_subnets
