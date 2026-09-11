from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    HnswConfigDiff,
    MatchValue,
    OptimizersConfigDiff,
    PointStruct,
    VectorParams,
)
from langchain_core.documents import Document

from backend.config.settings import settings


class VectorStoreManager:
    

    def __init__(self) -> None:
        self.config = settings.QDRANT_CONFIG
        self.collection_name = self.config["collection_name"]

        self.client = self._connect()

        if not self.collection_exists():
            self.create_collection()

    

    def _connect(self) -> QdrantClient:
        return QdrantClient(
            host=self.config["host"],
            port=self.config["port"],
        )

    

    def collection_exists(self) -> bool:
        collections = self.client.get_collections().collections
        return any(
            collection.name == self.collection_name
            for collection in collections
        )

    def create_collection(self) -> None:
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.config["vector_size"],
                    distance=Distance[self.config["distance"].upper()],
                ),
                hnsw_config=HnswConfigDiff(
                    **self.config["hnsw_config"]
                ),
                optimizers_config=OptimizersConfigDiff(
                    **self.config["optimizer_config"]
                ),
                on_disk_payload=self.config["on_disk_payload"],
                quantization_config=self.config["quantization"],
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="file_hash",
                field_schema="keyword",
            )

        except Exception as e:
            raise RuntimeError(
                f"Failed to create collection: {e}"
            )

    def delete_collection(self) -> None:
        self.client.delete_collection(
            collection_name=self.collection_name
        )

    def recreate_collection(self) -> None:
        if self.collection_exists():
            self.delete_collection()

        self.create_collection()

    

    def add_documents(
        self,
        documents: list[PointStruct],
        batch_size: int = 64,
    ) -> None:
        

        try:
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]

                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )

        except Exception as e:
            raise RuntimeError(
                f"Failed to insert documents: {e}"
            )
    def document_exists(
    self,
    file_hash: str,
    ) -> bool:
        """
        Check whether a document with the given file hash
        already exists in the collection.
        """
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_hash",
                            match=MatchValue(
                                value=file_hash,
                            ),
                        ),
                    ],
                ),
                limit=1,
            )

            return len(results) > 0

        except Exception as e:
            raise RuntimeError(
                f"Failed to check document existence: {e}"
            )


    

    def similarity_search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        query_filter: Filter | None = None,
    ) -> list[Document]:
        """
        Perform similarity search and return LangChain Documents.
        """

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k,
            )

            documents = []

            for point in results:
                payload = point.payload or {}

                documents.append(
                    Document(
                        page_content=payload.get("page_content")
                        or payload.get("content", ""),
                        metadata={
                            **payload,
                            "id": point.id,
                            "score": point.score,
                        },
                    )
                )

            return documents

        except Exception as e:
            raise RuntimeError(
                f"Similarity search failed: {e}"
            )

   

    def delete_documents(
        self,
        ids: list[str | int],
    ) -> None:

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids,
        )

   

    def get_collection_info(self) -> dict:

        info = self.client.get_collection(
            collection_name=self.collection_name
        )

        return {
            "name": self.collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status,
        }

    

    def health_check(self) -> bool:
        try:
            self.client.get_collection(
                self.collection_name
            )
            return True

        except Exception:
            return False