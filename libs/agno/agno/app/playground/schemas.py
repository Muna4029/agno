from __future__ import annotations

from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

from fastapi import UploadFile
from pydantic import BaseModel

from agno.agent import Agent
from agno.app.playground.operator import format_tools
from agno.memory.agent import AgentMemory
from agno.memory.team import TeamMemory
from agno.memory.v2 import Memory
from agno.team import Team


class AgentModel(BaseModel):
    name: str | None = None
    model: str | None = None
    provider: str | None = None


class AgentGetResponse(BaseModel):
    agent_id: str | None = None
    name: str | None = None
    model: AgentModel | None = None
    add_context: bool | None = None
    tools: list[dict[str, Any]] | None = None
    memory: dict[str, Any] | None = None
    storage: dict[str, Any] | None = None
    knowledge: dict[str, Any] | None = None
    description: str | None = None
    instructions: list[str] | str | Callable | None = None

    @classmethod
    def from_agent(self, agent: Agent, async_mode: bool = False) -> AgentGetResponse:
        if agent.memory:
            memory_dict: dict[str, Any] | None = {}
            if isinstance(agent.memory, AgentMemory) and agent.memory.db:
                memory_dict = {"name": agent.memory.db.__class__.__name__}
            elif isinstance(agent.memory, Memory) and agent.memory.db:
                memory_dict = {"name": "Memory"}
                if agent.memory.model is not None:
                    memory_dict["model"] = AgentModel(
                        name=agent.memory.model.name,
                        model=agent.memory.model.id,
                        provider=agent.memory.model.provider,
                    )
                if agent.memory.db is not None:
                    memory_dict["db"] = agent.memory.db.__dict__()  # type: ignore

            else:
                memory_dict = None
        else:
            memory_dict = None
        tools = agent.get_tools(session_id=str(uuid4()), async_mode=async_mode)
        return AgentGetResponse(
            agent_id=agent.agent_id,
            name=agent.name,
            model=AgentModel(
                name=agent.model.name or agent.model.__class__.__name__ if agent.model else None,
                model=agent.model.id if agent.model else None,
                provider=agent.model.provider or agent.model.__class__.__name__ if agent.model else None,
            ),
            add_context=agent.add_context,
            tools=format_tools(tools) if tools else None,
            memory=memory_dict,
            storage={"name": agent.storage.__class__.__name__} if agent.storage else None,
            knowledge={"name": agent.knowledge.__class__.__name__} if agent.knowledge else None,
            description=agent.description,
            instructions=agent.instructions,
        )


class AgentRunRequest(BaseModel):
    message: str
    agent_id: str
    stream: bool = True
    monitor: bool = False
    session_id: str | None = None
    user_id: str | None = None
    files: list[UploadFile] | None = None


class AgentRenameRequest(BaseModel):
    name: str
    user_id: str


class AgentSessionsResponse(BaseModel):
    title: str | None = None
    session_id: str | None = None
    session_name: str | None = None
    created_at: int | None = None


class MemoryResponse(BaseModel):
    memory: str
    topics: list[str] | None = None
    last_updated: datetime | None = None


class WorkflowRenameRequest(BaseModel):
    name: str


class WorkflowRunRequest(BaseModel):
    input: dict[str, Any]
    user_id: str | None = None
    session_id: str | None = None


class WorkflowSessionResponse(BaseModel):
    title: str | None = None
    session_id: str | None = None
    session_name: str | None = None
    created_at: int | None = None


class WorkflowGetResponse(BaseModel):
    workflow_id: str
    name: str | None = None
    description: str | None = None
    parameters: dict[str, Any] | None = None
    storage: str | None = None


class WorkflowsGetResponse(BaseModel):
    workflow_id: str
    name: str
    description: str | None = None


class TeamModel(BaseModel):
    name: str | None = None
    model: str | None = None
    provider: str | None = None


class TeamGetResponse(BaseModel):
    team_id: str | None = None
    name: str | None = None
    description: str | None = None
    mode: str | None = None
    model: TeamModel | None = None
    success_criteria: str | None = None
    instructions: list[str] | str | Callable | None = None
    members: list[AgentGetResponse | TeamGetResponse] | None = None
    expected_output: str | None = None
    context: str | None = None
    enable_agentic_context: bool | None = None
    storage: dict[str, Any] | None = None
    memory: dict[str, Any] | None = None
    async_mode: bool = False

    @classmethod
    def from_team(self, team: Team, async_mode: bool = False) -> TeamGetResponse:
        import json

        memory_dict: dict[str, Any] | None = {}
        if isinstance(team.memory, Memory):
            memory_dict = {"name": "Memory"}
            if team.memory.model is not None:
                memory_dict["model"] = AgentModel(
                    name=team.memory.model.name,
                    model=team.memory.model.id,
                    provider=team.memory.model.provider,
                )
            if team.memory.db is not None:
                memory_dict["db"] = team.memory.db.__dict__()  # type: ignore
        elif isinstance(team.memory, TeamMemory):
            memory_dict = {"name": team.memory.db.__class__.__name__}
        else:
            memory_dict = None

        return TeamGetResponse(
            team_id=team.team_id,
            name=team.name,
            model=TeamModel(
                name=team.model.name or team.model.__class__.__name__ if team.model else None,
                model=team.model.id if team.model else None,
                provider=team.model.provider or team.model.__class__.__name__ if team.model else None,
            ),
            success_criteria=team.success_criteria,
            instructions=team.instructions,
            description=team.description,
            expected_output=team.expected_output,
            context=json.dumps(team.context) if isinstance(team.context, dict) else team.context,
            enable_agentic_context=team.enable_agentic_context,
            mode=team.mode,
            storage={"name": team.storage.__class__.__name__} if team.storage else None,
            memory=memory_dict,
            members=[
                AgentGetResponse.from_agent(member, async_mode=async_mode)
                if isinstance(member, Agent)
                else TeamGetResponse.from_team(member, async_mode=async_mode)
                if isinstance(member, Team)
                else None
                for member in team.members
            ],
        )


class TeamRunRequest(BaseModel):
    input: dict[str, Any]
    user_id: str | None = None
    session_id: str | None = None
    files: list[UploadFile] | None = None


class TeamSessionResponse(BaseModel):
    title: str | None = None
    session_id: str | None = None
    session_name: str | None = None
    created_at: int | None = None


class TeamRenameRequest(BaseModel):
    name: str
    user_id: str
