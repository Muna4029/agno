from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from time import time
from typing import Any

from pydantic import BaseModel

from agno.media import AudioArtifact, AudioResponse, ImageArtifact, VideoArtifact
from agno.models.message import Citations, Message, MessageReferences
from agno.models.response import ToolExecution
from agno.reasoning.step import ReasoningStep
from agno.utils.log import logger


class RunEvent(str, Enum):
    """Events that can be sent by the run() functions"""

    run_started = "RunStarted"
    run_response = "RunResponse"
    run_completed = "RunCompleted"
    run_error = "RunError"
    run_cancelled = "RunCancelled"

    run_paused = "RunPaused"
    run_continued = "RunContinued"

    tool_call_started = "ToolCallStarted"
    tool_call_completed = "ToolCallCompleted"

    reasoning_started = "ReasoningStarted"
    reasoning_step = "ReasoningStep"
    reasoning_completed = "ReasoningCompleted"

    updating_memory = "UpdatingMemory"

    workflow_started = "WorkflowStarted"
    workflow_completed = "WorkflowCompleted"


@dataclass
class RunResponseExtraData:
    references: list[MessageReferences] | None = None
    add_messages: list[Message] | None = None
    reasoning_steps: list[ReasoningStep] | None = None
    reasoning_messages: list[Message] | None = None

    def to_dict(self) -> dict[str, Any]:
        _dict = {}
        if self.add_messages is not None:
            _dict["add_messages"] = [m.to_dict() for m in self.add_messages]
        if self.reasoning_messages is not None:
            _dict["reasoning_messages"] = [m.to_dict() for m in self.reasoning_messages]
        if self.reasoning_steps is not None:
            _dict["reasoning_steps"] = [rs.model_dump() for rs in self.reasoning_steps]
        if self.references is not None:
            _dict["references"] = [r.model_dump() for r in self.references]
        return _dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunResponseExtraData:
        add_messages = data.pop("add_messages", None)
        add_messages = [Message.model_validate(message) for message in add_messages] if add_messages else None

        reasoning_steps = data.pop("reasoning_steps", None)
        reasoning_steps = [ReasoningStep.model_validate(step) for step in reasoning_steps] if reasoning_steps else None

        reasoning_messages = data.pop("reasoning_messages", None)
        reasoning_messages = (
            [Message.model_validate(message) for message in reasoning_messages] if reasoning_messages else None
        )

        references = data.pop("references", None)
        references = [MessageReferences.model_validate(reference) for reference in references] if references else None

        return cls(
            add_messages=add_messages,
            reasoning_steps=reasoning_steps,
            reasoning_messages=reasoning_messages,
            references=references,
        )


@dataclass
class RunResponse:
    """Response returned by Agent.run() or Workflow.run() functions"""

    content: Any | None = None
    content_type: str = "str"
    thinking: str | None = None
    reasoning_content: str | None = None
    event: str = RunEvent.run_response.value
    messages: list[Message] | None = None
    metrics: dict[str, Any] | None = None
    model: str | None = None
    model_provider: str | None = None
    run_id: str | None = None
    agent_id: str | None = None
    session_id: str | None = None
    workflow_id: str | None = None
    tools: list[ToolExecution] | None = None
    formatted_tool_calls: list[str] | None = None
    images: list[ImageArtifact] | None = None  # Images attached to the response
    videos: list[VideoArtifact] | None = None  # Videos attached to the response
    audio: list[AudioArtifact] | None = None  # Audio attached to the response
    response_audio: AudioResponse | None = None  # Model audio response
    citations: Citations | None = None
    extra_data: RunResponseExtraData | None = None
    created_at: int = field(default_factory=lambda: int(time()))

    @property
    def is_paused(self):
        return self.event == RunEvent.run_paused

    @property
    def tools_requiring_confirmation(self):
        return [t for t in self.tools if t.requires_confirmation] if self.tools else []

    @property
    def tools_requiring_user_input(self):
        return [t for t in self.tools if t.requires_user_input] if self.tools else []

    @property
    def tools_awaiting_external_execution(self):
        return [t for t in self.tools if t.external_execution_required] if self.tools else []

    def to_dict(self) -> dict[str, Any]:
        _dict = {
            k: v
            for k, v in asdict(self).items()
            if v is not None
            and k not in ["messages", "tools", "extra_data", "images", "videos", "audio", "response_audio", "citations"]
        }
        if self.messages is not None:
            _dict["messages"] = [m.to_dict() for m in self.messages]

        if self.extra_data is not None:
            _dict["extra_data"] = (
                self.extra_data.to_dict() if isinstance(self.extra_data, RunResponseExtraData) else self.extra_data
            )

        if self.images is not None:
            _dict["images"] = []
            for img in self.images:
                if isinstance(img, ImageArtifact):
                    _dict["images"].append(img.to_dict())
                else:
                    _dict["images"].append(img)

        if self.videos is not None:
            _dict["videos"] = []
            for vid in self.videos:
                if isinstance(vid, VideoArtifact):
                    _dict["videos"].append(vid.to_dict())
                else:
                    _dict["videos"].append(vid)

        if self.audio is not None:
            _dict["audio"] = []
            for aud in self.audio:
                if isinstance(aud, AudioArtifact):
                    _dict["audio"].append(aud.to_dict())
                else:
                    _dict["audio"].append(aud)

        if self.response_audio is not None:
            if isinstance(self.response_audio, AudioResponse):
                _dict["response_audio"] = self.response_audio.to_dict()
            else:
                _dict["response_audio"] = self.response_audio

        if self.citations is not None:
            if isinstance(self.citations, Citations):
                _dict["citations"] = self.citations.model_dump(exclude_none=True)
            else:
                _dict["citations"] = self.citations

        if self.content and isinstance(self.content, BaseModel):
            _dict["content"] = self.content.model_dump(exclude_none=True)

        if self.tools is not None:
            _dict["tools"] = []
            for tool in self.tools:
                if isinstance(tool, ToolExecution):
                    _dict["tools"].append(tool.to_dict())
                else:
                    _dict["tools"].append(tool)

        return _dict

    def to_json(self) -> str:
        import json

        try:
            _dict = self.to_dict()
        except Exception:
            logger.error("Failed to convert response to json", exc_info=True)
            raise

        return json.dumps(_dict, indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunResponse:
        messages = data.pop("messages", None)
        messages = [Message.model_validate(message) for message in messages] if messages else None
        tools = data.pop("tools", None)
        tools = [ToolExecution.from_dict(tool) for tool in tools] if tools else None
        return cls(messages=messages, tools=tools, **data)

    def get_content_as_string(self, **kwargs) -> str:
        import json

        from pydantic import BaseModel

        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, BaseModel):
            return self.content.model_dump_json(exclude_none=True, **kwargs)
        else:
            return json.dumps(self.content, **kwargs)
