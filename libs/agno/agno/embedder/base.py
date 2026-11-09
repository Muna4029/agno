from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Embedder:
    """Base class for managing embedders"""

    dimensions: int | None = 1536

    def get_embedding(self, text: str) -> list[float]:
        raise NotImplementedError

    def get_embedding_and_usage(self, text: str) -> tuple[list[float], dict | None]:
        raise NotImplementedError
