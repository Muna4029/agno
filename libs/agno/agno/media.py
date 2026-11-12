from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


class Media(BaseModel):
    id: str
    original_prompt: str | None = None
    revised_prompt: str | None = None


class VideoArtifact(Media):
    url: str | None = None  # Remote location for file (if no inline content)
    content: str | bytes | None = None  # type: ignore
    mime_type: str | None = None  # MIME type of the video content
    eta: str | None = None
    length: str | None = None

    def to_dict(self) -> dict[str, Any]:
        response_dict = {
            "id": self.id,
            "url": self.url,
            "content": self.content
            if isinstance(self.content, str)
            else self.content.decode("utf-8")
            if self.content
            else None,
            "mime_type": self.mime_type,
            "eta": self.eta,
        }
        return {k: v for k, v in response_dict.items() if v is not None}


class ImageArtifact(Media):
    url: str | None = None  # Remote location for file
    content: bytes | None = None  # Actual image bytes content
    mime_type: str | None = None
    alt_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        response_dict = {
            "id": self.id,
            "url": self.url,
            "content": self.content.decode("utf-8")
            if self.content and isinstance(self.content, bytes)
            else self.content,
            "mime_type": self.mime_type,
            "alt_text": self.alt_text,
        }
        return {k: v for k, v in response_dict.items() if v is not None}


class AudioArtifact(Media):
    url: str | None = None  # Remote location for file
    base64_audio: str | None = None  # Base64-encoded audio data
    length: str | None = None
    mime_type: str | None = None

    @model_validator(mode="before")
    def validate_exclusive_audio(cls, data: Any):
        """
        Ensure that either `url` or `base64_audio` is provided, but not both.
        """
        if data.get("url") and data.get("base64_audio"):
            raise ValueError("Provide either `url` or `base64_audio`, not both.")
        if not data.get("url") and not data.get("base64_audio"):
            raise ValueError("Either `url` or `base64_audio` must be provided.")
        return data

    def to_dict(self) -> dict[str, Any]:
        response_dict = {
            "id": self.id,
            "url": self.url,
            "content": self.base64_audio,
            "mime_type": self.mime_type,
            "length": self.length,
        }
        return {k: v for k, v in response_dict.items() if v is not None}


class Video(BaseModel):
    filepath: Path | str | None = None  # Absolute local location for video
    content: Any | None = None  # Actual video bytes content
    url: str | None = None  # Remote location for video
    format: str | None = None  # E.g. `mp4`, `mov`, `avi`, `mkv`, `webm`, `flv`, `mpeg`, `mpg`, `wmv`, `three_gp`

    @model_validator(mode="before")
    def validate_data(cls, data: Any):
        """
        Ensure that exactly one of `filepath`, or `content` or `url` is provided.
        Also converts content to bytes if it's a string.
        """
        # Extract the values from the input data
        filepath = data.get("filepath")
        content = data.get("content")
        url = data.get("url")

        # Convert and decompress content to bytes if it's a string
        if content and isinstance(content, str):
            import base64

            try:
                import zlib

                decoded_content = base64.b64decode(content)
                content = zlib.decompress(decoded_content)
            except Exception:
                content = base64.b64decode(content).decode("utf-8")
        data["content"] = content

        # Count how many fields are set (not None)
        count = len([field for field in [filepath, content, url] if field is not None])

        if count == 0:
            raise ValueError("One of `filepath` or `content` or `url` must be provided.")
        elif count > 1:
            raise ValueError("Only one of `filepath` or `content` or `url` should be provided.")

        return data

    def to_dict(self) -> dict[str, Any]:
        import base64
        import zlib

        response_dict = {
            "content": base64.b64encode(
                zlib.compress(self.content) if isinstance(self.content, bytes) else self.content.encode("utf-8")
            ).decode("utf-8")
            if self.content
            else None,
            "filepath": self.filepath,
            "format": self.format,
        }
        return {k: v for k, v in response_dict.items() if v is not None}

    @classmethod
    def from_artifact(cls, artifact: VideoArtifact) -> Video:
        return cls(url=artifact.url)


class Audio(BaseModel):
    content: Any | None = None  # Actual audio bytes content
    filepath: Path | str | None = None  # Absolute local location for audio
    url: str | None = None  # Remote location for audio
    format: str | None = None

    @model_validator(mode="before")
    def validate_data(cls, data: Any):
        """
        Ensure that exactly one of `filepath`, or `content` is provided.
        Also converts content to bytes if it's a string.
        """
        # Extract the values from the input data
        filepath = data.get("filepath")
        content = data.get("content")
        url = data.get("url")

        # Convert and decompress content to bytes if it's a string
        if content and isinstance(content, str):
            import base64

            try:
                import zlib

                decoded_content = base64.b64decode(content)
                content = zlib.decompress(decoded_content)
            except Exception:
                content = base64.b64decode(content).decode("utf-8")
        data["content"] = content

        # Count how many fields are set (not None)
        count = len([field for field in [filepath, content, url] if field is not None])

        if count == 0:
            raise ValueError("One of `filepath` or `content` or `url` must be provided.")
        elif count > 1:
            raise ValueError("Only one of `filepath` or `content` or `url` should be provided.")

        return data

    @property
    def audio_url_content(self) -> bytes | None:
        import httpx

        if self.url:
            return httpx.get(self.url).content
        else:
            return None

    def to_dict(self) -> dict[str, Any]:
        import base64
        import zlib

        response_dict = {
            "content": base64.b64encode(
                zlib.compress(self.content) if isinstance(self.content, bytes) else self.content.encode("utf-8")
            ).decode("utf-8")
            if self.content
            else None,
            "filepath": self.filepath,
            "format": self.format,
        }

        return {k: v for k, v in response_dict.items() if v is not None}

    @classmethod
    def from_artifact(cls, artifact: AudioArtifact) -> Audio:
        return cls(url=artifact.url, content=artifact.base64_audio, format=artifact.mime_type)


class AudioResponse(BaseModel):
    id: str | None = None
    content: str | None = None  # Base64 encoded
    expires_at: int | None = None
    transcript: str | None = None

    mime_type: str | None = None
    sample_rate: int | None = 24000
    channels: int | None = 1

    def to_dict(self) -> dict[str, Any]:
        import base64

        response_dict = {
            "id": self.id,
            "content": base64.b64encode(self.content).decode("utf-8")
            if isinstance(self.content, bytes)
            else self.content,
            "expires_at": self.expires_at,
            "transcript": self.transcript,
            "mime_type": self.mime_type,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
        }
        return {k: v for k, v in response_dict.items() if v is not None}


class Image(BaseModel):
    url: str | None = None  # Remote location for image
    filepath: Path | str | None = None  # Absolute local location for image
    content: Any | None = None  # Actual image bytes content
    format: str | None = None  # E.g. `png`, `jpeg`, `webp`, `gif`
    detail: str | None = (
        None  # low, medium, high or auto (per OpenAI spec https://platform.openai.com/docs/guides/vision?lang=node#low-or-high-fidelity-image-understanding)
    )
    id: str | None = None

    @property
    def image_url_content(self) -> bytes | None:
        import httpx

        if self.url:
            return httpx.get(self.url).content
        else:
            return None

    @model_validator(mode="before")
    def validate_data(cls, data: Any):
        """
        Ensure that exactly one of `url`, `filepath`, or `content` is provided.
        Also converts content to bytes if it's a string.
        """
        # Extract the values from the input data
        url = data.get("url")
        filepath = data.get("filepath")
        content = data.get("content")

        # Convert and decompress content to bytes if it's a string
        if content and isinstance(content, str):
            import base64

            try:
                import zlib

                decoded_content = base64.b64decode(content)
                content = zlib.decompress(decoded_content)
            except Exception:
                content = base64.b64decode(content).decode("utf-8")
        data["content"] = content

        # Count how many fields are set (not None)
        count = len([field for field in [url, filepath, content] if field is not None])

        if count == 0:
            raise ValueError("One of `url`, `filepath`, or `content` must be provided.")
        elif count > 1:
            raise ValueError("Only one of `url`, `filepath`, or `content` should be provided.")

        return data

    def to_dict(self) -> dict[str, Any]:
        import base64
        import zlib

        response_dict = {
            "content": base64.b64encode(
                zlib.compress(self.content) if isinstance(self.content, bytes) else self.content.encode("utf-8")
            ).decode("utf-8")
            if self.content
            else None,
            "filepath": self.filepath,
            "url": self.url,
            "detail": self.detail,
        }

        return {k: v for k, v in response_dict.items() if v is not None}

    @classmethod
    def from_artifact(cls, artifact: ImageArtifact) -> Image:
        return cls(url=artifact.url)


class File(BaseModel):
    url: str | None = None
    filepath: Path | str | None = None
    # Raw bytes content of a file
    content: Any | None = None
    mime_type: str | None = None
    # External file object (e.g. GeminiFile, must be a valid object as expected by the model you are using)
    external: Any | None = None

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_source(cls, data):
        """Ensure at least one of url, filepath, or content is provided."""
        if isinstance(data, dict) and not any(data.get(field) for field in ["url", "filepath", "content", "external"]):
            raise ValueError("At least one of url, filepath, content or external must be provided")
        return data

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v):
        """Validate that the mime_type is one of the allowed types."""
        if v is not None and v not in cls.valid_mime_types():
            raise ValueError(f"Invalid MIME type: {v}. Must be one of: {cls.valid_mime_types()}")
        return v

    @classmethod
    def valid_mime_types(cls) -> list[str]:
        return [
            "application/pdf",
            "application/x-javascript",
            "text/javascript",
            "application/x-python",
            "text/x-python",
            "text/plain",
            "text/html",
            "text/css",
            "text/md",
            "text/csv",
            "text/xml",
            "text/rtf",
        ]

    @property
    def file_url_content(self) -> tuple[bytes, str] | None:
        import httpx

        if self.url:
            response = httpx.get(self.url)
            content = response.content
            mime_type = response.headers.get("Content-Type", "").split(";")[0]
            return content, mime_type
        else:
            return None
