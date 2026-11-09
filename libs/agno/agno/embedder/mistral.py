from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import Any

from agno.embedder.base import Embedder
from agno.utils.log import logger

try:
    from mistralai import Mistral
    from mistralai.models.embeddingresponse import EmbeddingResponse
except ImportError:
    raise ImportError("`mistralai` not installed")


@dataclass
class MistralEmbedder(Embedder):
    id: str = "mistral-embed"
    dimensions: int = 1024
    # -*- Request parameters
    request_params: dict[str, Any] | None = None
    # -*- Client parameters
    api_key: str | None = getenv("MISTRAL_API_KEY")
    endpoint: str | None = None
    max_retries: int | None = None
    timeout: int | None = None
    client_params: dict[str, Any] | None = None
    # -*- Provide the Mistral Client manually
    mistral_client: Mistral | None = None

    @property
    def client(self) -> Mistral:
        if self.mistral_client:
            return self.mistral_client

        _client_params: dict[str, Any] = {
            "api_key": self.api_key,
            "endpoint": self.endpoint,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
        }
        _client_params = {k: v for k, v in _client_params.items() if v is not None}

        if self.client_params:
            _client_params.update(self.client_params)

        self.mistral_client = Mistral(**_client_params)

        return self.mistral_client

    def _response(self, text: str) -> EmbeddingResponse:
        _request_params: dict[str, Any] = {
            "inputs": text,
            "model": self.id,
        }
        if self.request_params:
            _request_params.update(self.request_params)
        response = self.client.embeddings.create(**_request_params)
        if response is None:
            raise ValueError("Failed to get embedding response")
        return response

    def get_embedding(self, text: str) -> list[float]:
        try:
            response: EmbeddingResponse = self._response(text=text)
            if response.data and response.data[0].embedding:
                return response.data[0].embedding
            return []
        except Exception as e:
            logger.warning(f"Error getting embedding: {e}")
            return []

    def get_embedding_and_usage(self, text: str) -> tuple[list[float], dict[str, Any]]:
        try:
            response: EmbeddingResponse = self._response(text=text)
            embedding: list[float] = (
                response.data[0].embedding if (response.data and response.data[0].embedding) else []
            )
            usage: dict[str, Any] = response.usage.model_dump() if response.usage else {}
            return embedding, usage
        except Exception as e:
            logger.warning(f"Error getting embedding and usage: {e}")
            return [], {}
