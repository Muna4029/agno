from __future__ import annotations

import io
from collections.abc import AsyncIterator, Iterator
from typing import IO

from pydantic import Field

from agno.document import Document
from agno.document.reader.pdf_reader import PDFImageReader, PDFReader
from agno.knowledge.agent import AgentKnowledge


class PDFBytesKnowledgeBase(AgentKnowledge):
    pdfs: list[bytes] | list[IO]

    exclude_files: list[str] = Field(default_factory=list)

    reader: PDFReader | PDFImageReader = PDFReader()

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        """Iterate over PDFs bytes and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for pdf in self.pdfs:
            _pdf = io.BytesIO(pdf) if isinstance(pdf, bytes) else pdf
            yield self.reader.read(pdf=_pdf)

    @property
    async def async_document_lists(self) -> AsyncIterator[list[Document]]:
        """Iterate over PDFs bytes and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for pdf in self.pdfs:
            _pdf = io.BytesIO(pdf) if isinstance(pdf, bytes) else pdf
            yield await self.reader.async_read(pdf=_pdf)
