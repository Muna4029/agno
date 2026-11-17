from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from agno.aws.resource.s3.bucket import S3Bucket  # type: ignore
from agno.aws.resource.s3.object import S3Object  # type: ignore
from agno.document import Document
from agno.knowledge.agent import AgentKnowledge


class S3KnowledgeBase(AgentKnowledge):
    # Provide either bucket or bucket_name
    bucket: S3Bucket | None = None
    bucket_name: str | None = None

    # Provide either object or key
    key: str | None = None
    object: S3Object | None = None

    # Filter objects by prefix
    # Ignored if object or key is provided
    prefix: str | None = None

    @property
    def document_lists(self) -> Iterator[list[Document]]:
        raise NotImplementedError

    @property
    def async_document_lists(self) -> AsyncIterator[list[Document]]:
        raise NotImplementedError

    @property
    def s3_objects(self) -> list[S3Object]:
        """Iterate over PDFs in a s3 bucket and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        s3_objects_to_read: list[S3Object] = []

        if self.bucket is None and self.bucket_name is None:
            raise ValueError("No bucket or bucket_name provided")

        if self.bucket is not None and self.bucket_name is not None:
            raise ValueError("Provide either bucket or bucket_name")

        if self.object is not None and self.key is not None:
            raise ValueError("Provide either object or key")

        if self.bucket_name is not None:
            self.bucket = S3Bucket(name=self.bucket_name)

        if self.bucket is not None:
            if self.key is not None:
                _object = S3Object(bucket_name=self.bucket.name, name=self.key)
                s3_objects_to_read.append(_object)
            elif self.object is not None:
                s3_objects_to_read.append(self.object)
            elif self.prefix is not None:
                s3_objects_to_read.extend(self.bucket.get_objects(prefix=self.prefix))
            else:
                s3_objects_to_read.extend(self.bucket.get_objects())

        return s3_objects_to_read
