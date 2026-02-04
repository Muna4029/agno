from __future__ import annotations

from hashlib import md5
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

try:
    from qdrant_client import AsyncQdrantClient, QdrantClient
    from qdrant_client.http import models
except ImportError as e:
    raise ImportError(
        "The `qdrant-client` package is not installed. Please install it via `pip install qdrant-client`."
    ) from e

if TYPE_CHECKING:
    # fastembed often ships without type stubs in many environments
    pass  # type: ignore[import-not-found]

from agno.document import Document
from agno.embedder import Embedder
from agno.reranker.base import Reranker
from agno.utils.log import log_debug, log_info
from agno.vectordb.base import VectorDb
from agno.vectordb.distance import Distance
from agno.vectordb.search import SearchType

DEFAULT_DENSE_VECTOR_NAME = "dense"
DEFAULT_SPARSE_VECTOR_NAME = "sparse"
DEFAULT_SPARSE_MODEL = "Qdrant/bm25"


class Qdrant(VectorDb):
    """Vector DB implementation powered by Qdrant - https://qdrant.tech/"""

    def __init__(
        self,
        collection: str,
        embedder: Optional[Embedder] = None,
        distance: Distance = Distance.cosine,
        location: Optional[str] = None,
        url: Optional[str] = None,
        port: Optional[int] = 6333,
        grpc_port: int = 6334,
        prefer_grpc: bool = False,
        https: Optional[bool] = None,
        api_key: Optional[str] = None,
        prefix: Optional[str] = None,
        timeout: Optional[float] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        reranker: Optional[Reranker] = None,
        search_type: SearchType = SearchType.vector,
        dense_vector_name: str = DEFAULT_DENSE_VECTOR_NAME,
        sparse_vector_name: str = DEFAULT_SPARSE_VECTOR_NAME,
        hybrid_fusion_strategy: models.Fusion = models.Fusion.RRF,
        fastembed_kwargs: Optional[dict] = None,
        **kwargs: Any,
    ):
        """
        Args:
            collection (str): Name of the Qdrant collection.
            embedder (Optional[Embedder]): Optional embedder for automatic vector generation.
            distance (Distance): Distance metric to use (default: cosine).
            location (Optional[str]): `":memory:"` for in-memory, or str used as `url`. If `None`, use default host/port.
            url (Optional[str]): Full URL (scheme, host, port, prefix). Overrides host/port if provided.
            port (Optional[int]): REST API port (default: 6333).
            grpc_port (int): gRPC interface port (default: 6334).
            prefer_grpc (bool): Prefer gRPC over REST if True.
            https (Optional[bool]): Use HTTPS if True.
            api_key (Optional[str]): API key for Qdrant Cloud authentication.
            prefix (Optional[str]): URL path prefix (e.g., "service/v1").
            timeout (Optional[float]): Request timeout (REST: default 5s, gRPC: unlimited).
            host (Optional[str]): Qdrant host (default: "localhost" if not specified).
            path (Optional[str]): Path for local persistence (QdrantLocal).
            reranker (Optional[Reranker]): Optional reranker for result refinement.
            search_type (SearchType): Whether to use vector, keyword or hybrid search.
            dense_vector_name (str): Dense vector name.
            sparse_vector_name (str): Sparse vector name.
            hybrid_fusion_strategy (models.Fusion): Strategy for hybrid fusion.
            fastembed_kwargs (Optional[dict]): Keyword args for `fastembed.SparseTextEmbedding.__init__()`.
            **kwargs: Keyword args for `qdrant_client.QdrantClient.__init__()`.
        """
        self.collection: str = collection

        if embedder is None:
            from agno.embedder.openai import OpenAIEmbedder

            embedder = OpenAIEmbedder()
            log_info("Embedder not provided, using OpenAIEmbedder as default.")

        self.embedder: Embedder = embedder
        self.dimensions: Optional[int] = self.embedder.dimensions

        self.distance: Distance = distance

        self._client: Optional[QdrantClient] = None
        self._async_client: Optional[AsyncQdrantClient] = None

        self.location: Optional[str] = location
        self.url: Optional[str] = url
        self.port: Optional[int] = port
        self.grpc_port: int = grpc_port
        self.prefer_grpc: bool = prefer_grpc
        self.https: Optional[bool] = https
        self.api_key: Optional[str] = api_key
        self.prefix: Optional[str] = prefix
        self.timeout: Optional[float] = timeout
        self.host: Optional[str] = host
        self.path: Optional[str] = path

        self.reranker: Optional[Reranker] = reranker

        self.kwargs: Dict[str, Any] = dict(kwargs)

        self.search_type: SearchType = search_type
        self.dense_vector_name: str = dense_vector_name
        self.sparse_vector_name: str = sparse_vector_name
        self.hybrid_fusion_strategy: models.Fusion = hybrid_fusion_strategy

        # Backward compatibility for unnamed vectors.
        # Named vectors are used for hybrid.
        self.use_named_vectors: bool = search_type in [SearchType.hybrid]

        if self.search_type in [SearchType.keyword, SearchType.hybrid]:
            try:
                from fastembed import SparseTextEmbedding  # type: ignore[import-not-found]

                default_kwargs = {"model_name": DEFAULT_SPARSE_MODEL}
                if fastembed_kwargs:
                    default_kwargs.update(fastembed_kwargs)

                # Keep runtime type flexible since fastembed typing is often missing
                self.sparse_encoder: Any = SparseTextEmbedding(**default_kwargs)
            except ImportError as e:
                raise ImportError(
                    "To use keyword/hybrid search, install the `fastembed` extra with "
                    "`pip install 'qdrant-client[fastembed]'`."
                ) from e

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            log_debug("Creating Qdrant Client")
            self._client = QdrantClient(
                location=self.location,
                url=self.url,
                port=self.port,
                grpc_port=self.grpc_port,
                prefer_grpc=self.prefer_grpc,
                https=self.https,
                api_key=self.api_key,
                prefix=self.prefix,
                timeout=int(self.timeout) if self.timeout is not None else None,
                host=self.host,
                path=self.path,
                **self.kwargs,
            )
        return self._client

    @property
    def async_client(self) -> AsyncQdrantClient:
        if self._async_client is None:
            log_debug("Creating Async Qdrant Client")
            self._async_client = AsyncQdrantClient(
                location=self.location,
                url=self.url,
                port=self.port,
                grpc_port=self.grpc_port,
                prefer_grpc=self.prefer_grpc,
                https=self.https,
                api_key=self.api_key,
                prefix=self.prefix,
                timeout=int(self.timeout) if self.timeout is not None else None,
                host=self.host,
                path=self.path,
                **self.kwargs,
            )
        return self._async_client

    def create(self) -> None:
        _distance = models.Distance.COSINE
        if self.distance == Distance.l2:
            _distance = models.Distance.EUCLID
        elif self.distance == Distance.max_inner_product:
            _distance = models.Distance.DOT

        if not self.exists():
            log_debug(f"Creating collection: {self.collection}")

            if self.search_type == SearchType.vector:
                vectors_config: Any = models.VectorParams(size=self.dimensions, distance=_distance)
            else:
                vectors_config = {self.dense_vector_name: models.VectorParams(size=self.dimensions, distance=_distance)}

            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=vectors_config,
                sparse_vectors_config={self.sparse_vector_name: models.SparseVectorParams()}
                if self.search_type in [SearchType.keyword, SearchType.hybrid]
                else None,
            )

    async def async_create(self) -> None:
        _distance = models.Distance.COSINE
        if self.distance == Distance.l2:
            _distance = models.Distance.EUCLID
        elif self.distance == Distance.max_inner_product:
            _distance = models.Distance.DOT

        if not await self.async_exists():
            log_debug(f"Creating collection asynchronously: {self.collection}")

            if self.search_type == SearchType.vector:
                vectors_config: Any = models.VectorParams(size=self.dimensions, distance=_distance)
            else:
                vectors_config = {self.dense_vector_name: models.VectorParams(size=self.dimensions, distance=_distance)}

            await self.async_client.create_collection(
                collection_name=self.collection,
                vectors_config=vectors_config,
                sparse_vectors_config={self.sparse_vector_name: models.SparseVectorParams()}
                if self.search_type in [SearchType.keyword, SearchType.hybrid]
                else None,
            )

    def doc_exists(self, document: Document) -> bool:
        if self.client:
            cleaned_content = document.content.replace("\x00", "\ufffd")
            doc_id = md5(cleaned_content.encode()).hexdigest()
            collection_points = self.client.retrieve(
                collection_name=self.collection,
                ids=[doc_id],
            )
            return len(collection_points) > 0
        return False

    async def async_doc_exists(self, document: Document) -> bool:
        cleaned_content = document.content.replace("\x00", "\ufffd")
        doc_id = md5(cleaned_content.encode()).hexdigest()
        collection_points = await self.async_client.retrieve(
            collection_name=self.collection,
            ids=[doc_id],
        )
        return len(collection_points) > 0

    def name_exists(self, name: str) -> bool:
        if self.client:
            scroll_result = self.client.scroll(
                collection_name=self.collection,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="name", match=models.MatchValue(value=name))]
                ),
                limit=1,
            )
            return len(scroll_result[0]) > 0
        return False

    async def async_name_exists(self, name: str) -> bool:
        if self.async_client:
            scroll_result = await self.async_client.scroll(
                collection_name=self.collection,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="name", match=models.MatchValue(value=name))]
                ),
                limit=1,
            )
            return len(scroll_result[0]) > 0
        return False

    def insert(self, documents: List[Document], filters: Optional[Dict[str, Any]] = None, batch_size: int = 10) -> None:
        log_debug(f"Inserting {len(documents)} documents")
        points: List[models.PointStruct] = []

        for document in documents:
            cleaned_content = document.content.replace("\x00", "\ufffd")
            doc_id = md5(cleaned_content.encode()).hexdigest()

            # Qdrant PointStruct.vector accepts either:
            # - dense vector as List[float] (unnamed vectors, backward compat)
            # - dict of named vectors including sparse objects
            vector: Union[List[float], Dict[str, Any]]

            if self.search_type == SearchType.vector:
                document.embed(embedder=self.embedder)
                if document.embedding is None:
                    raise ValueError("Document embedding is None after embedding.")
                vector = document.embedding
            else:
                vector = {}

                if self.search_type == SearchType.hybrid:
                    document.embed(embedder=self.embedder)
                    if document.embedding is None:
                        raise ValueError("Document embedding is None after embedding.")
                    vector[self.dense_vector_name] = document.embedding

                if self.search_type in [SearchType.keyword, SearchType.hybrid]:
                    vector[self.sparse_vector_name] = next(self.sparse_encoder.embed([document.content])).as_object()

            payload: Dict[str, Any] = {
                "name": document.name,
                "meta_data": document.meta_data,
                "content": cleaned_content,
                "usage": document.usage,
            }

            if filters:
                payload.setdefault("meta_data", {})
                payload["meta_data"].update(filters)

            points.append(
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload,
                )
            )

            log_debug(f"Inserted document: {document.name} ({document.meta_data})")

        if points:
            self.client.upsert(collection_name=self.collection, wait=False, points=points)

        log_debug(f"Upsert {len(points)} documents")

    async def async_insert(self, documents: List[Document], filters: Optional[Dict[str, Any]] = None) -> None:
        log_debug(f"Inserting {len(documents)} documents asynchronously")

        import asyncio

        async def process_document(document: Document) -> models.PointStruct:
            cleaned_content = document.content.replace("\x00", "\ufffd")
            doc_id = md5(cleaned_content.encode()).hexdigest()

            vector: Union[List[float], Dict[str, Any]]

            if self.search_type == SearchType.vector:
                document.embed(embedder=self.embedder)
                if document.embedding is None:
                    raise ValueError("Document embedding is None after embedding.")
                vector = document.embedding
            else:
                vector = {}

                if self.search_type == SearchType.hybrid:
                    document.embed(embedder=self.embedder)
                    if document.embedding is None:
                        raise ValueError("Document embedding is None after embedding.")
                    vector[self.dense_vector_name] = document.embedding

                if self.search_type in [SearchType.keyword, SearchType.hybrid]:
                    vector[self.sparse_vector_name] = next(self.sparse_encoder.embed([document.content])).as_object()

            payload: Dict[str, Any] = {
                "name": document.name,
                "meta_data": document.meta_data,
                "content": cleaned_content,
                "usage": document.usage,
            }

            if filters:
                payload.setdefault("meta_data", {})
                payload["meta_data"].update(filters)

            log_debug(f"Inserted document asynchronously: {document.name} ({document.meta_data})")

            return models.PointStruct(
                id=doc_id,
                vector=vector,
                payload=payload,
            )

        points = await asyncio.gather(*[process_document(doc) for doc in documents])

        if points:
            await self.async_client.upsert(collection_name=self.collection, wait=False, points=points)

        log_debug(f"Upserted {len(points)} documents asynchronously")

    def upsert(self, documents: List[Document], filters: Optional[Dict[str, Any]] = None) -> None:
        log_debug("Redirecting the request to insert")
        self.insert(documents, filters)

    async def async_upsert(self, documents: List[Document], filters: Optional[Dict[str, Any]] = None) -> None:
        log_debug("Redirecting the async request to async_insert")
        await self.async_insert(documents, filters)

    def search(self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        qfilter = self._format_filters(filters)

        if self.search_type == SearchType.vector:
            results = self._run_vector_search_sync(query, limit, qfilter)
        elif self.search_type == SearchType.keyword:
            results = self._run_keyword_search_sync(query, limit, qfilter)
        elif self.search_type == SearchType.hybrid:
            results = self._run_hybrid_search_sync(query, limit, qfilter)
        else:
            raise ValueError(f"Unsupported search type: {self.search_type}")

        return self._build_search_results(results, query)

    async def async_search(self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        qfilter = self._format_filters(filters)

        if self.search_type == SearchType.vector:
            results = await self._run_vector_search_async(query, limit, qfilter)
        elif self.search_type == SearchType.keyword:
            results = await self._run_keyword_search_async(query, limit, qfilter)
        elif self.search_type == SearchType.hybrid:
            results = await self._run_hybrid_search_async(query, limit, qfilter)
        else:
            raise ValueError(f"Unsupported search type: {self.search_type}")

        return self._build_search_results(results, query)

    def _run_hybrid_search_sync(
        self,
        query: str,
        limit: int,
        filters: Optional[models.Filter],
    ) -> List[models.ScoredPoint]:
        dense_embedding = self.embedder.get_embedding(query)
        sparse_embedding = next(self.sparse_encoder.embed([query])).as_object()

        call = self.client.query_points(
            collection_name=self.collection,
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(**sparse_embedding),
                    limit=limit,
                    using=self.sparse_vector_name,
                ),
                models.Prefetch(query=dense_embedding, limit=limit, using=self.dense_vector_name),
            ],
            query=models.FusionQuery(fusion=self.hybrid_fusion_strategy),
            with_vectors=True,
            with_payload=True,
            limit=limit,
            query_filter=filters,
        )
        return call.points

    def _run_vector_search_sync(
        self,
        query: str,
        limit: int,
        filters: Optional[models.Filter],
    ) -> List[models.ScoredPoint]:
        dense_embedding = self.embedder.get_embedding(query)

        if self.use_named_vectors:
            call = self.client.query_points(
                collection_name=self.collection,
                query=dense_embedding,
                with_vectors=True,
                with_payload=True,
                limit=limit,
                query_filter=filters,
                using=self.dense_vector_name,
            )
        else:
            call = self.client.query_points(
                collection_name=self.collection,
                query=dense_embedding,
                with_vectors=True,
                with_payload=True,
                limit=limit,
                query_filter=filters,
            )

        return call.points

    def _run_keyword_search_sync(
        self,
        query: str,
        limit: int,
        filters: Optional[models.Filter],
    ) -> List[models.ScoredPoint]:
        sparse_embedding = next(self.sparse_encoder.embed([query])).as_object()
        call = self.client.query_points(
            collection_name=self.collection,
            query=models.SparseVector(**sparse_embedding),
            with_vectors=True,
            with_payload=True,
            limit=limit,
            using=self.sparse_vector_name,
            query_filter=filters,
        )
        return call.points

    async def _run_vector_search_async(
        self,
        query: str,
        limit: int,
        filters: Optional[models.Filter],
    ) -> List[models.ScoredPoint]:
        dense_embedding = self.embedder.get_embedding(query)

        if self.use_named_vectors:
            call = await self.async_client.query_points(
                collection_name=self.collection,
                query=dense_embedding,
                with_vectors=True,
                with_payload=True,
                limit=limit,
                query_filter=filters,
                using=self.dense_vector_name,
            )
        else:
            call = await self.async_client.query_points(
                collection_name=self.collection,
                query=dense_embedding,
                with_vectors=True,
                with_payload=True,
                limit=limit,
                query_filter=filters,
            )

        return call.points

    async def _run_keyword_search_async(
        self,
        query: str,
        limit: int,
        filters: Optional[models.Filter],
    ) -> List[models.ScoredPoint]:
        sparse_embedding = next(self.sparse_encoder.embed([query])).as_object()
        call = await self.async_client.query_points(
            collection_name=self.collection,
            query=models.SparseVector(**sparse_embedding),
            with_vectors=True,
            with_payload=True,
            limit=limit,
            using=self.sparse_vector_name,
            query_filter=filters,
        )
        return call.points

    async def _run_hybrid_search_async(
        self,
        query: str,
        limit: int,
        filters: Optional[models.Filter],
    ) -> List[models.ScoredPoint]:
        dense_embedding = self.embedder.get_embedding(query)
        sparse_embedding = next(self.sparse_encoder.embed([query])).as_object()

        call = await self.async_client.query_points(
            collection_name=self.collection,
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(**sparse_embedding),
                    limit=limit,
                    using=self.sparse_vector_name,
                ),
                models.Prefetch(query=dense_embedding, limit=limit, using=self.dense_vector_name),
            ],
            query=models.FusionQuery(fusion=self.hybrid_fusion_strategy),
            with_vectors=True,
            with_payload=True,
            limit=limit,
            query_filter=filters,
        )
        return call.points

    def _build_search_results(self, results: List[models.ScoredPoint], query: str) -> List[Document]:
        search_results: List[Document] = []

        for result in results:
            if result.payload is None:
                continue

            search_results.append(
                Document(
                    name=result.payload["name"],
                    meta_data=result.payload["meta_data"],
                    content=result.payload["content"],
                    embedder=self.embedder,
                    embedding=result.vector,  # type: ignore[arg-type]
                    usage=result.payload["usage"],
                )
            )

        if self.reranker:
            search_results = self.reranker.rerank(query=query, documents=search_results)

        log_info(f"Found {len(search_results)} documents")
        return search_results

    def _format_filters(self, filters: Optional[Dict[str, Any]]) -> Optional[models.Filter]:
        if not filters:
            return None

        filter_conditions: List[models.FieldCondition] = []
        for key, value in filters.items():
            if "." not in key and not key.startswith("meta_data."):
                key = f"meta_data.{key}"

            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=f"{key}.{sub_key}",
                            match=models.MatchValue(value=sub_value),
                        )
                    )
            else:
                filter_conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value),
                    )
                )

        if not filter_conditions:
            return None

        return models.Filter(must=filter_conditions)

    def drop(self) -> None:
        if self.exists():
            log_debug(f"Deleting collection: {self.collection}")
            self.client.delete_collection(self.collection)

    async def async_drop(self) -> None:
        if await self.async_exists():
            log_debug(f"Deleting collection asynchronously: {self.collection}")
            await self.async_client.delete_collection(self.collection)

    def exists(self) -> bool:
        return self.client.collection_exists(collection_name=self.collection)

    async def async_exists(self) -> bool:
        return await self.async_client.collection_exists(collection_name=self.collection)

    def get_count(self) -> int:
        count_result: models.CountResult = self.client.count(collection_name=self.collection, exact=True)
        return count_result.count

    def optimize(self) -> None:
        pass

    def delete(self) -> bool:
        return self.client.delete_collection(collection_name=self.collection)
