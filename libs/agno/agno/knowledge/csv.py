from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator, Iterator

from pydantic import Field

from agno.document import Document
from agno.document.reader.csv_reader import CSVReader
from agno.knowledge.agent import AgentKnowledge


class CSVKnowledgeBase(AgentKnowledge):
    path: str | Path
    exclude_files: list[str] = Field(default_factory=list)
    reader: CSVReader = CSVReader()

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        """Iterate over CSVs and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        _csv_path: Path = Path(self.path) if isinstance(self.path, str) else self.path

        if _csv_path.exists() and _csv_path.is_dir():
            for _csv in _csv_path.glob("**/*.csv"):
                if _csv.name in self.exclude_files:
                    continue
                yield self.reader.read(file=_csv)
        elif _csv_path.exists() and _csv_path.is_file() and _csv_path.suffix == ".csv":
            if _csv_path.name in self.exclude_files:
                return
            yield self.reader.read(file=_csv_path)

    @property
    async def async_document_lists(self) -> AsyncIterator[list[Document]]:
        _csv_path: Path = Path(self.path) if isinstance(self.path, str) else self.path

        if _csv_path.exists() and _csv_path.is_dir():
            for _csv in _csv_path.glob("**/*.csv"):
                if _csv.name in self.exclude_files:
                    continue
                yield await self.reader.async_read(file=_csv)
        elif _csv_path.exists() and _csv_path.is_file() and _csv_path.suffix == ".csv":
            if _csv_path.name in self.exclude_files:
                return
            yield await self.reader.async_read(file=_csv_path)
