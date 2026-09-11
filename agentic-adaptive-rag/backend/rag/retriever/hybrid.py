from collections import defaultdict
from langchain_core.documents import Document

from backend.rag.retriever.bm25 import SparseRetriever
from backend.rag.retriever.vector import VectorRetriver

class HybridRetriever:
    def __init__(
        self,
        sparse_retriever: SparseRetriever,
        vector_retriever: VectorRetriver,
        rrf_k: int = 60,
    ) -> None:
        self.sparse_retriever = sparse_retriever
        self.vector_retriever = vector_retriever
        self.rrf_k = rrf_k
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Document]:
        sparse_results = self.sparse_retriever.retrieve(query, top_k)
        vector_results = self.vector_retriever.retrive(query, top_k)

        fused_results=self._rrf_fusion(
            vector_results,
            sparse_results,
        )
        return fused_results[:top_k]
    def _rrf_fusion(
        self,
        vector_results: list[Document],
        sparse_results: list[Document],
    ) -> list[Document]:
        

        scores = defaultdict(float)
        documents = {}

        
        for rank, document in enumerate(vector_results, start=1):
            doc_id = self._document_id(document)

            scores[doc_id] += 1 / (self.rrf_k + rank)
            documents[doc_id] = document

       
        for rank, document in enumerate(sparse_results, start=1):
            doc_id = self._document_id(document)

            scores[doc_id] += 1 / (self.rrf_k + rank)
            documents[doc_id] = document

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            documents[doc_id]
            for doc_id, _ in ranked
        ]

    @staticmethod
    def _document_id(document: Document) -> str:
        

        return (
            document.metadata.get("chunk_id")
            or document.metadata.get("id")
            or hash(document.page_content)
        )
        

    