from collections.abc import Iterator

from agno.document import Document
from agno.knowledge.agent import AgentKnowledge

try:
    import wikipedia
except ImportError:
    raise ImportError("The `wikipedia` package is not installed. Please install it via `pip install wikipedia`.")


class WikipediaKnowledgeBase(AgentKnowledge):
    topics: list[str] = []
    auto_suggest: bool = True

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        """Iterate over urls and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        for topic in self.topics:
            yield [
                Document(
                    name=topic,
                    meta_data={"topic": topic},
                    content=wikipedia.summary(topic, auto_suggest=self.auto_suggest),
                )
            ]
