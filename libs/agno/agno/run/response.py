from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from time import time
from typing import Any, Union

from pydantic import BaseModel

from agno.media import AudioArtifact, AudioResponse, ImageArtifact, VideoArtifact
from agno.models.message import Citations, Message
from agno.models.response import ToolExecution
from agno.run.base import BaseRunResponseEvent, RunResponseExtraData, RunStatus
from agno.utils.log import logger


class RunEvent(str, Enum):
    """Events that can be sent by the run() functions"""

    run_started = "RunStarted"
    run_response_content = "RunResponseContent"
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

    memory_update_started = "MemoryUpdateStarted"
    memory_update_completed = "MemoryUpdateCompleted"

    parser_model_response_started = "ParserModelResponseStarted"
    parser_model_response_completed = "ParserModelResponseCompleted"


@dataclass
class BaseAgentRunResponseEvent(BaseRunResponseEvent):
    created_at: int = field(default_factory=lambda: int(time()))
    event: str = ""
    agent_id: str = ""
    agent_name: str = ""
    run_id: str | None = None
    session_id: str | None = None
    team_session_id: str | None = None

    # For backwards compatibility
    content: Any | None = None


@dataclass
class RunResponseStartedEvent(BaseAgentRunResponseEvent):
    """Event sent when the run starts"""

    event: str = RunEvent.run_started.value
    model: str = ""
    model_provider: str = ""


@dataclass
class RunResponseContentEvent(BaseAgentRunResponseEvent):
    """Main event for each delta of the RunResponse"""

    event: str = RunEvent.run_response_content.value
    content: Any | None = None
    content_type: str = "str"
    thinking: str | None = None
    citations: Citations | None = None
    response_audio: AudioResponse | None = None  # Model audio response
    image: ImageArtifact | None = None  # Image attached to the response
    extra_data: RunResponseExtraData | None = None


@dataclass
class RunResponseCompletedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.run_completed.value
    content: Any | None = None
    content_type: str = "str"
    reasoning_content: str | None = None
    thinking: str | None = None
    citations: Citations | None = None
    images: list[ImageArtifact] | None = None  # Images attached to the response
    videos: list[VideoArtifact] | None = None  # Videos attached to the response
    audio: list[AudioArtifact] | None = None  # Audio attached to the response
    response_audio: AudioResponse | None = None  # Model audio response
    extra_data: RunResponseExtraData | None = None


@dataclass
class RunResponsePausedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.run_paused.value
    tools: list[ToolExecution] | None = None

    @property
    def is_paused(self):
        return True


@dataclass
class RunResponseContinuedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.run_continued.value


@dataclass
class RunResponseErrorEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.run_error.value
    content: str | None = None


@dataclass
class RunResponseCancelledEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.run_cancelled.value
    reason: str | None = None

    @property
    def is_cancelled(self):
        return True


@dataclass
class MemoryUpdateStartedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.memory_update_started.value


@dataclass
class MemoryUpdateCompletedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.memory_update_completed.value


@dataclass
class ReasoningStartedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.reasoning_started.value


@dataclass
class ReasoningStepEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.reasoning_step.value
    content: Any | None = None
    content_type: str = "str"
    reasoning_content: str = ""


@dataclass
class ReasoningCompletedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.reasoning_completed.value
    content: Any | None = None
    content_type: str = "str"


@dataclass
class ToolCallStartedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.tool_call_started.value
    tool: ToolExecution | None = None


@dataclass
class ToolCallCompletedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.tool_call_completed.value
    tool: ToolExecution | None = None
    content: Any | None = None
    images: list[ImageArtifact] | None = None  # Images produced by the tool call
    videos: list[VideoArtifact] | None = None  # Videos produced by the tool call
    audio: list[AudioArtifact] | None = None  # Audio produced by the tool call


@dataclass
class ParserModelResponseStartedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.parser_model_response_started.value


@dataclass
class ParserModelResponseCompletedEvent(BaseAgentRunResponseEvent):
    event: str = RunEvent.parser_model_response_completed.value


RunResponseEvent = Union[
    RunResponseStartedEvent,
    RunResponseContentEvent,
    RunResponseCompletedEvent,
    RunResponseErrorEvent,
    RunResponseCancelledEvent,
    RunResponsePausedEvent,
    RunResponseContinuedEvent,
    ReasoningStartedEvent,
    ReasoningStepEvent,
    ReasoningCompletedEvent,
    MemoryUpdateStartedEvent,
    MemoryUpdateCompletedEvent,
    ToolCallStartedEvent,
    ToolCallCompletedEvent,
    ParserModelResponseStartedEvent,
    ParserModelResponseCompletedEvent,
]


# Map event string to dataclass
RUN_EVENT_TYPE_REGISTRY = {
    RunEvent.run_started.value: RunResponseStartedEvent,
    RunEvent.run_response_content.value: RunResponseContentEvent,
    RunEvent.run_completed.value: RunResponseCompletedEvent,
    RunEvent.run_error.value: RunResponseErrorEvent,
    RunEvent.run_cancelled.value: RunResponseCancelledEvent,
    RunEvent.run_paused.value: RunResponsePausedEvent,
    RunEvent.run_continued.value: RunResponseContinuedEvent,
    RunEvent.reasoning_started.value: ReasoningStartedEvent,
    RunEvent.reasoning_step.value: ReasoningStepEvent,
    RunEvent.reasoning_completed.value: ReasoningCompletedEvent,
    RunEvent.memory_update_started.value: MemoryUpdateStartedEvent,
    RunEvent.memory_update_completed.value: MemoryUpdateCompletedEvent,
    RunEvent.tool_call_started.value: ToolCallStartedEvent,
    RunEvent.tool_call_completed.value: ToolCallCompletedEvent,
    RunEvent.parser_model_response_started.value: ParserModelResponseStartedEvent,
    RunEvent.parser_model_response_completed.value: ParserModelResponseCompletedEvent,
}


def run_response_event_from_dict(data: dict) -> BaseRunResponseEvent:
    event_type = data.get("event", "")
    cls = RUN_EVENT_TYPE_REGISTRY.get(event_type)
    if not cls:
        raise ValueError(f"Unknown event type: {event_type}")
    return cls.from_dict(data)  # type: ignore


@dataclass
class RunResponse:
    """Response returned by Agent.run() or Workflow.run() functions"""

    content: Any | None = None
    content_type: str = "str"
    thinking: str | None = None
    reasoning_content: str | None = None
    messages: list[Message] | None = None
    metrics: dict[str, Any] | None = None
    model: str | None = None
    model_provider: str | None = None
    run_id: str | None = None
    agent_id: str | None = None
    agent_name: str | None = None
    session_id: str | None = None
    team_session_id: str | None = None
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

    events: list[RunResponseEvent] | None = None

    status: RunStatus = RunStatus.running

    @property
    def is_paused(self):
        return self.status == RunStatus.paused

    @property
    def is_cancelled(self):
        return self.status == RunStatus.cancelled

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
            and k
            not in [
                "messages",
                "tools",
                "extra_data",
                "images",
                "videos",
                "audio",
                "response_audio",
                "citations",
                "events",
            ]
        }

        if self.events is not None:
            _dict["events"] = [e.to_dict() for e in self.events]

        if self.status is not None:
            _dict["status"] = self.status.value if isinstance(self.status, RunStatus) else self.status

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
            _dict["content"] = self.content.model_dump(exclude_none=True, mode="json")

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
        events = data.pop("events", None)
        events = [run_response_event_from_dict(event) for event in events] if events else None

        messages = data.pop("messages", None)
        messages = [Message.model_validate(message) for message in messages] if messages else None

        tools = data.pop("tools", None)
        tools = [ToolExecution.from_dict(tool) for tool in tools] if tools else None

        images = data.pop("images", None)
        images = [ImageArtifact.model_validate(image) for image in images] if images else None

        videos = data.pop("videos", None)
        videos = [VideoArtifact.model_validate(video) for video in videos] if videos else None

        audio = data.pop("audio", None)
        audio = [AudioArtifact.model_validate(audio) for audio in audio] if audio else None

        response_audio = data.pop("response_audio", None)
        response_audio = AudioResponse.model_validate(response_audio) if response_audio else None

        # To make it backwards compatible
        if "event" in data:
            data.pop("event")

        return cls(
            messages=messages,
            tools=tools,
            images=images,
            audio=audio,
            videos=videos,
            response_audio=response_audio,
            events=events,
            **data,
        )

    def get_content_as_string(self, **kwargs) -> str:
        import json

        from pydantic import BaseModel

        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, BaseModel):
            return self.content.model_dump_json(exclude_none=True, **kwargs)
        else:
            return json.dumps(self.content, **kwargs)
