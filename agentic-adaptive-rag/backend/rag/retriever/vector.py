from typing import Any
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vector import VectorStoreManager

class VectorRetriver:

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        vector_store: VectorStoreManager,
    ) -> None:

        self.embedding_manager = embedding_manager
        self.vector_store = vector_store
    def retrive(
            self,query: str,top_k: int = 5, 
    )-> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Query cannot be empty or whitespace.")

        query_vector = self.embedding_manager.embed_query(query)
        results = self.vector_store.similarity_search(
            query_vector=query_vector,
            top_k=top_k,
        )
        return results