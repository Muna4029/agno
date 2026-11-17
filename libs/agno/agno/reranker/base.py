from pydantic import BaseModel, ConfigDict

from agno.document import Document


class Reranker(BaseModel):
    """Base class for rerankers"""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    def rerank(self, query: str, documents: list[Document]) -> list[Document]:
        raise NotImplementedError
