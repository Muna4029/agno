from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from agno.document.base import Document
from agno.document.chunking.fixed import FixedSizeChunking
from agno.document.chunking.strategy import ChunkingStrategy


@dataclass
class Reader:
    """Base class for reading documents"""

    chunk: bool = True
    chunk_size: int = 5000
    separators: list[str] = field(default_factory=lambda: ["\n", "\n\n", "\r", "\r\n", "\n\r", "\t", " ", "  "])
    chunking_strategy: ChunkingStrategy | None = None

    def __init__(
        self, chunk: bool = True, chunk_size: int = 5000, chunking_strategy: ChunkingStrategy | None = None
    ) -> None:
        self.chunk = chunk
        self.chunk_size = chunk_size
        self.chunking_strategy = chunking_strategy

    def read(self, obj: Any) -> list[Document]:
        raise NotImplementedError

    async def async_read(self, obj: Any) -> list[Document]:
        raise NotImplementedError

    def chunk_document(self, document: Document) -> list[Document]:
        if self.chunking_strategy is None:
            self.chunking_strategy = FixedSizeChunking(chunk_size=self.chunk_size)
        return self.chunking_strategy.chunk(document)  # type: ignore

    async def chunk_documents_async(self, documents: list[Document]) -> list[Document]:
        """
        Asynchronously chunk a list of documents using the instance's chunk_document method.

        Args:
            documents: List of documents to be chunked.

        Returns:
            A flattened list of chunked documents.
        """

        async def _chunk_document_async(doc: Document) -> list[Document]:
            return await asyncio.to_thread(self.chunk_document, doc)

        # Process chunking in parallel for all documents
        chunked_lists = await asyncio.gather(*[_chunk_document_async(doc) for doc in documents])
        # Flatten the result
        return [chunk for sublist in chunked_lists for chunk in sublist]
