from collections.abc import AsyncIterator, Iterator

from agno.document import Document
from agno.knowledge.agent import AgentKnowledge


class DocumentKnowledgeBase(AgentKnowledge):
    documents: list[Document]

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        """Iterate over documents and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for _document in self.documents:
            yield [_document]

    @property
    async def async_document_lists(self) -> AsyncIterator[list[Document]]:
        """Iterate over documents and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for _document in self.documents:
            yield [_document]
