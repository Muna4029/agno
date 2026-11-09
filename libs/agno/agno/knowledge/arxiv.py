from collections.abc import AsyncIterator, Iterator

from agno.document import Document
from agno.document.reader.arxiv_reader import ArxivReader
from agno.knowledge.agent import AgentKnowledge


class ArxivKnowledgeBase(AgentKnowledge):
    queries: list[str] = []
    reader: ArxivReader = ArxivReader()

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        """Iterate over urls and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for _query in self.queries:
            yield self.reader.read(query=_query)

    @property
    async def async_document_lists(self) -> AsyncIterator[list[Document]]:
        """Iterate over queries and yield lists of documents asynchronously.
        Each object yielded by the iterator is a list of documents.

        Returns:
            AsyncIterator[List[Document]]: Async iterator yielding list of documents
        """
        for _query in self.queries:
            yield await self.reader.async_read(query=_query)
