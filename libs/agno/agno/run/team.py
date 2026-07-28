from __future__ import annotations

from dataclasses import asdict, dataclass, field
from time import time
from typing import Any

from pydantic import BaseModel

from agno.media import AudioArtifact, AudioResponse, ImageArtifact, VideoArtifact
from agno.models.message import Citations, Message
from agno.models.response import ToolExecution
from agno.run.response import RunEvent, RunResponse, RunResponseExtraData


@dataclass
class TeamRunResponse:
    """Response returned by Team.run() functions"""

    event: str = RunEvent.run_response.value

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
    session_id: str | None = None

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

        _dict = self.to_dict()

        return json.dumps(_dict, indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TeamRunResponse:
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

        return cls(
            messages=messages,
            member_responses=parsed_member_responses,
            extra_data=extra_data,
            images=images,
            videos=videos,
            audio=audio,
            response_audio=response_audio,
            tools=tools,
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
