from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agno.embedder import Embedder


@dataclass
class Document:
    """Dataclass for managing a document"""

    content: str
    id: str | None = None
    name: str | None = None
    meta_data: dict[str, Any] = field(default_factory=dict)
    embedder: Embedder | None = None
    embedding: list[float] | None = None
    usage: dict[str, Any] | None = None
    reranking_score: float | None = None

    def embed(self, embedder: Embedder | None = None) -> None:
        """Embed the document using the provided embedder"""

        _embedder = embedder or self.embedder
        if _embedder is None:
            raise ValueError("No embedder provided")

        self.embedding, self.usage = _embedder.get_embedding_and_usage(self.content)

    def to_dict(self) -> dict[str, Any]:
        """Returns a dictionary representation of the document"""
        fields = {"name", "meta_data", "content"}
        return {
            field: getattr(self, field)
            for field in fields
            if getattr(self, field) is not None or field == "content"  # content is always included
        }

    @classmethod
    def from_dict(cls, document: dict[str, Any]) -> Document:
        """Returns a Document object from a dictionary representation"""
        return cls(**document)

    @classmethod
    def from_json(cls, document: str) -> Document:
        """Returns a Document object from a json string representation"""
        import json

        return cls(**json.loads(document))
