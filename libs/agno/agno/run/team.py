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
from agno.run.response import RunEvent, RunResponse, RunResponseEvent, run_response_event_from_dict


class TeamRunEvent(str, Enum):
    """Events that can be sent by the run() functions"""

    run_started = "TeamRunStarted"
    run_response_content = "TeamRunResponseContent"
    run_completed = "TeamRunCompleted"
    run_error = "TeamRunError"
    run_cancelled = "TeamRunCancelled"

    tool_call_started = "TeamToolCallStarted"
    tool_call_completed = "TeamToolCallCompleted"

    reasoning_started = "TeamReasoningStarted"
    reasoning_step = "TeamReasoningStep"
    reasoning_completed = "TeamReasoningCompleted"

    memory_update_started = "TeamMemoryUpdateStarted"
    memory_update_completed = "TeamMemoryUpdateCompleted"

    parser_model_response_started = "TeamParserModelResponseStarted"
    parser_model_response_completed = "TeamParserModelResponseCompleted"


@dataclass
class BaseTeamRunResponseEvent(BaseRunResponseEvent):
    created_at: int = field(default_factory=lambda: int(time()))
    event: str = ""
    team_id: str = ""
    team_name: str = ""
    run_id: str | None = None
    session_id: str | None = None
    # If the team is a member of a team, this will be the session id of the parent team
    team_session_id: str | None = None

    # For backwards compatibility
    content: Any | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseTeamRunResponseEvent:
        member_responses = data.pop("member_responses", None)
        event = super().from_dict(data)

        member_responses_final = []
        for response in member_responses or []:
            if "agent_id" in response:
                run_response_parsed = RunResponse.from_dict(response)
            else:
                run_response_parsed = TeamRunResponse.from_dict(response)  # type: ignore
            member_responses_final.append(run_response_parsed)

        if member_responses_final:
            event.member_responses = member_responses_final

        return event


@dataclass
class RunResponseStartedEvent(BaseTeamRunResponseEvent):
    """Event sent when the run starts"""

    event: str = TeamRunEvent.run_started.value
    model: str = ""
    model_provider: str = ""


@dataclass
class RunResponseContentEvent(BaseTeamRunResponseEvent):
    """Main event for each delta of the RunResponse"""

    event: str = TeamRunEvent.run_response_content.value
    content: Any | None = None
    content_type: str = "str"
    thinking: str | None = None
    citations: Citations | None = None
    response_audio: AudioResponse | None = None  # Model audio response
    image: ImageArtifact | None = None  # Image attached to the response
    extra_data: RunResponseExtraData | None = None


@dataclass
class RunResponseCompletedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.run_completed.value
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
    member_responses: list[TeamRunResponse | RunResponse] = field(default_factory=list)


@dataclass
class RunResponseErrorEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.run_error.value
    content: str | None = None


@dataclass
class RunResponseCancelledEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.run_cancelled.value
    reason: str | None = None


@dataclass
class MemoryUpdateStartedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.memory_update_started.value


@dataclass
class MemoryUpdateCompletedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.memory_update_completed.value


@dataclass
class ReasoningStartedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.reasoning_started.value


@dataclass
class ReasoningStepEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.reasoning_step.value
    content: Any | None = None
    content_type: str = "str"
    reasoning_content: str = ""


@dataclass
class ReasoningCompletedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.reasoning_completed.value
    content: Any | None = None
    content_type: str = "str"


@dataclass
class ToolCallStartedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.tool_call_started.value
    tool: ToolExecution | None = None


@dataclass
class ToolCallCompletedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.tool_call_completed.value
    tool: ToolExecution | None = None
    content: Any | None = None
    images: list[ImageArtifact] | None = None  # Images produced by the tool call
    videos: list[VideoArtifact] | None = None  # Videos produced by the tool call
    audio: list[AudioArtifact] | None = None  # Audio produced by the tool call


@dataclass
class ParserModelResponseStartedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.parser_model_response_started.value


@dataclass
class ParserModelResponseCompletedEvent(BaseTeamRunResponseEvent):
    event: str = TeamRunEvent.parser_model_response_completed.value


TeamRunResponseEvent = Union[
    RunResponseStartedEvent,
    RunResponseContentEvent,
    RunResponseCompletedEvent,
    RunResponseErrorEvent,
    RunResponseCancelledEvent,
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

# Map event string to dataclass for team events
TEAM_RUN_EVENT_TYPE_REGISTRY = {
    TeamRunEvent.run_started.value: RunResponseStartedEvent,
    TeamRunEvent.run_response_content.value: RunResponseContentEvent,
    TeamRunEvent.run_completed.value: RunResponseCompletedEvent,
    TeamRunEvent.run_error.value: RunResponseErrorEvent,
    TeamRunEvent.run_cancelled.value: RunResponseCancelledEvent,
    TeamRunEvent.reasoning_started.value: ReasoningStartedEvent,
    TeamRunEvent.reasoning_step.value: ReasoningStepEvent,
    TeamRunEvent.reasoning_completed.value: ReasoningCompletedEvent,
    TeamRunEvent.memory_update_started.value: MemoryUpdateStartedEvent,
    TeamRunEvent.memory_update_completed.value: MemoryUpdateCompletedEvent,
    TeamRunEvent.tool_call_started.value: ToolCallStartedEvent,
    TeamRunEvent.tool_call_completed.value: ToolCallCompletedEvent,
    TeamRunEvent.parser_model_response_started.value: ParserModelResponseStartedEvent,
    TeamRunEvent.parser_model_response_completed.value: ParserModelResponseCompletedEvent,
}


def team_run_response_event_from_dict(data: dict) -> BaseTeamRunResponseEvent:
    event_type = data.get("event", "")
    if event_type in {e.value for e in RunEvent}:
        return run_response_event_from_dict(data)  # type: ignore
    else:
        event_class = TEAM_RUN_EVENT_TYPE_REGISTRY.get(event_type)
    if not event_class:
        raise ValueError(f"Unknown team event type: {event_type}")
    return event_class.from_dict(data)  # type: ignore


@dataclass
class TeamRunResponse:
    """Response returned by Team.run() functions"""

    content: Any | None = None
    content_type: str = "str"
    thinking: str | None = None
    messages: list[Message] | None = None
    metrics: dict[str, Any] | None = None
    model: str | None = None
    model_provider: str | None = None

    member_responses: list[TeamRunResponse | RunResponse] = field(default_factory=list)

    run_id: str | None = None
    team_id: str | None = None
    team_name: str | None = None
    session_id: str | None = None
    # If the team is a member of a team, this will be the session id of the parent team
    team_session_id: str | None = None

    tools: list[ToolExecution] | None = None
    formatted_tool_calls: list[str] | None = None

    images: list[ImageArtifact] | None = None  # Images from member runs
    videos: list[VideoArtifact] | None = None  # Videos from member runs
    audio: list[AudioArtifact] | None = None  # Audio from member runs

    response_audio: AudioResponse | None = None  # Model audio response

    reasoning_content: str | None = None

    citations: Citations | None = None

    extra_data: RunResponseExtraData | None = None
    created_at: int = field(default_factory=lambda: int(time()))

    events: list[RunResponseEvent | TeamRunResponseEvent] | None = None

    status: RunStatus = RunStatus.running

    @property
    def is_paused(self):
        return self.status == RunStatus.paused

    @property
    def is_cancelled(self):
        return self.status == RunStatus.cancelled

    def to_dict(self) -> dict[str, Any]:
        _dict = {
            k: v
            for k, v in asdict(self).items()
            if v is not None
            and k
            not in [
                "messages",
                "status",
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
            _dict["extra_data"] = self.extra_data.to_dict()

        if self.images is not None:
            _dict["images"] = [img.to_dict() for img in self.images]

        if self.videos is not None:
            _dict["videos"] = [vid.to_dict() for vid in self.videos]

        if self.audio is not None:
            _dict["audio"] = [aud.to_dict() for aud in self.audio]

        if self.response_audio is not None:
            _dict["response_audio"] = self.response_audio.to_dict()

        if self.member_responses:
            _dict["member_responses"] = [response.to_dict() for response in self.member_responses]

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

        _dict = self.to_dict()

        return json.dumps(_dict, indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TeamRunResponse:
        events = data.pop("events", None)
        final_events = []
        for event in events or []:
            if "agent_id" in event:
                # Use the factory from response.py for agent events
                from agno.run.response import run_response_event_from_dict

                event = run_response_event_from_dict(event)
            else:
                event = team_run_response_event_from_dict(event)
            final_events.append(event)
        events = final_events

        messages = data.pop("messages", None)
        messages = [Message.model_validate(message) for message in messages] if messages else None

        member_responses = data.pop("member_responses", None)
        parsed_member_responses: list[TeamRunResponse | RunResponse] = []
        if member_responses is not None:
            for response in member_responses:
                if "agent_id" in response:
                    parsed_member_responses.append(RunResponse.from_dict(response))
                else:
                    parsed_member_responses.append(cls.from_dict(response))

        extra_data = data.pop("extra_data", None)
        if extra_data is not None:
            extra_data = RunResponseExtraData.from_dict(extra_data)

        images = data.pop("images", None)
        images = [ImageArtifact.model_validate(image) for image in images] if images else None

        videos = data.pop("videos", None)
        videos = [VideoArtifact.model_validate(video) for video in videos] if videos else None

        audio = data.pop("audio", None)
        audio = [AudioArtifact.model_validate(audio) for audio in audio] if audio else None

        tools = data.pop("tools", None)
        tools = [ToolExecution.from_dict(tool) for tool in tools] if tools else None

        response_audio = data.pop("response_audio", None)
        response_audio = AudioResponse.model_validate(response_audio) if response_audio else None

        # To make it backwards compatible
        if "event" in data:
            data.pop("event")

        return cls(
            messages=messages,
            member_responses=parsed_member_responses,
            extra_data=extra_data,
            images=images,
            videos=videos,
            audio=audio,
            response_audio=response_audio,
            tools=tools,
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

    def add_member_run(self, run_response: TeamRunResponse | RunResponse) -> None:
        self.member_responses.append(run_response)
        if run_response.images is not None:
            if self.images is None:
                self.images = []
            self.images.extend(run_response.images)
        if run_response.videos is not None:
            if self.videos is None:
                self.videos = []
            self.videos.extend(run_response.videos)
        if run_response.audio is not None:
            if self.audio is None:
                self.audio = []
            self.audio.extend(run_response.audio)
