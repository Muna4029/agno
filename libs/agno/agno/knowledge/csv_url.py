from __future__ import annotations

from typing import AsyncIterator, Iterator

from agno.document import Document
from agno.document.reader.csv_reader import CSVUrlReader
from agno.knowledge.agent import AgentKnowledge
from agno.utils.log import logger


class CSVUrlKnowledgeBase(AgentKnowledge):
    urls: list[str]
    reader: CSVUrlReader = CSVUrlReader()

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        for url in self.urls:
            if url.endswith(".csv"):
                yield self.reader.read(url=url)
            else:
                logger.error(f"Unsupported URL: {url}")

    @property
    async def async_document_lists(self) -> AsyncIterator[list[Document]]:
        for url in self.urls:
            if url.endswith(".csv"):
                yield await self.reader.async_read(url=url)
            else:
                logger.error(f"Unsupported URL: {url}")
