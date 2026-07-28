from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agno.embedder.base import Embedder
from agno.utils.log import logger

try:
    from voyageai import Client as VoyageClient
    from voyageai.object import EmbeddingsObject
except ImportError:
    raise ImportError("`voyageai` not installed. Please install using `pip install voyageai`")


@dataclass
class VoyageAIEmbedder(Embedder):
    id: str = "voyage-2"
    dimensions: int = 1024
    request_params: dict[str, Any] | None = None
    api_key: str | None = None
    base_url: str = "https://api.voyageai.com/v1/embeddings"
    max_retries: int | None = None
    timeout: float | None = None
    client_params: dict[str, Any] | None = None
    voyage_client: VoyageClient | None = None

    @property
    def client(self) -> VoyageClient:
        if self.voyage_client:
            return self.voyage_client

        _client_params = {
            "api_key": self.api_key,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
        }
        _client_params = {k: v for k, v in _client_params.items() if v is not None}
        if self.client_params:
            _client_params.update(self.client_params)
        self.voyage_client = VoyageClient(**_client_params)
        return self.voyage_client

    def _response(self, text: str) -> EmbeddingsObject:
        _request_params: dict[str, Any] = {
            "texts": [text],
            "model": self.id,
        }
        if self.request_params:
            _request_params.update(self.request_params)
        return self.client.embed(**_request_params)

    def get_embedding(self, text: str) -> list[float]:
        response: EmbeddingsObject = self._response(text=text)
        try:
            return response.embeddings[0]
        except Exception as e:
            logger.warning(e)
            return []

    def get_embedding_and_usage(self, text: str) -> tuple[list[float], dict | None]:
        response: EmbeddingsObject = self._response(text=text)

        embedding = response.embeddings[0]
        usage = {"total_tokens": response.total_tokens}
        return embedding, usage
