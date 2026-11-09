from __future__ import annotations

from dataclasses import dataclass

from agno.embedder.base import Embedder
from agno.utils.log import logger

try:
    import numpy as np

except ImportError:
    raise ImportError("numpy not installed, use `pip install numpy`")


try:
    from fastembed import TextEmbedding  # type: ignore

except ImportError:
    raise ImportError("fastembed not installed, use pip install fastembed")


@dataclass
class FastEmbedEmbedder(Embedder):
    """Using BAAI/bge-small-en-v1.5 model, more models available: https://qdrant.github.io/fastembed/examples/Supported_Models/"""

    id: str = "BAAI/bge-small-en-v1.5"
    dimensions: int = 384

    def get_embedding(self, text: str) -> list[float]:
        model = TextEmbedding(model_name=self.id)
        embeddings = model.embed(text)
        embedding_list = next(iter(embeddings))
        if isinstance(embedding_list, np.ndarray):
            return embedding_list.tolist()

        try:
            return list(embedding_list)
        except Exception as e:
            logger.warning(e)
            return []

    def get_embedding_and_usage(self, text: str) -> tuple[list[float], dict | None]:
        embedding = self.get_embedding(text=text)
        # Currently, FastEmbed does not provide usage information
        usage = None

        return embedding, usage
