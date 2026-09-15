from __future__ import annotations

from dataclasses import dataclass
from os import getenv

from agno.embedder.openai import OpenAIEmbedder


@dataclass
class FireworksEmbedder(OpenAIEmbedder):
    id: str = "nomic-ai/nomic-embed-text-v1.5"
    dimensions: int = 768
    api_key: str | None = getenv("FIREWORKS_API_KEY")
    base_url: str = "https://api.fireworks.ai/inference/v1"
