from langchain_core.documents import Document

from backend.config.settings import settings
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vector import VectorStoreManager
from backend.rag.retriever.vector import VectorRetriver
from backend.rag.retriever.bm25 import SparseRetriever
from backend.rag.retriever.hybrid import HybridRetriever
from backend.rag.retriever.mqr import MultiQueryRetriever
from backend.rag.retriever.reranker import Reranker
from backend.rag.prompts.prompt_builder import PromptBuilder
from backend.rag.llm.llm import LLMManager


# Minimum reranker score to consider retrieval acceptable.
# If the top document falls below this threshold, the pipeline
# falls back to MQR for a second retrieval attempt.
QUALITY_THRESHOLD = 0.4


class RAGPipeline:
    """
    End-to-end RAG query pipeline.

    Flow:
        1. Embed the user query.
        2. Run hybrid retrieval (dense + BM25 via RRF).
        3. Rerank retrieved documents with a cross-encoder.
        4. Check retrieval quality against a score threshold.
        5. If quality is poor, fall back to MQR and re-retrieve.
        6. Build the final prompt and generate an answer.
    """

    def __init__(self) -> None:
        # Core components
        self.embedding_manager = EmbeddingManager()
        self.vector_store = VectorStoreManager()
        self.llm = LLMManager()

        # Retrievers
        self.sparse_retriever = SparseRetriever()
        self.vector_retriever = VectorRetriver(
            embedding_manager=self.embedding_manager,
            vector_store=self.vector_store,
        )
        self.hybrid_retriever = HybridRetriever(
            sparse_retriever=self.sparse_retriever,
            vector_retriever=self.vector_retriever,
        )
        self.mqr = MultiQueryRetriever()
        self.reranker = Reranker()

        # Config
        self.top_k = settings.reranker_config["TOP_K"]

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, query: str) -> dict:
        """
        Run the full RAG pipeline for a user query.

        Args:
            query: The user's question.

        Returns:
            dict with keys:
                - answer:    The generated answer string.
                - sources:   List of source metadata dicts.
                - strategy:  Retrieval strategy used ("hybrid" or "mqr_fallback").
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # Step 1 — Hybrid retrieval
        documents = self._hybrid_retrieve(query)

        # Step 2 — Rerank
        reranked = self.reranker.rerank(query=query, documents=documents)

        # Step 3 — Quality check; fall back to MQR if needed
        strategy = "hybrid"
        if not self._quality_ok(reranked):
            documents = self._mqr_retrieve(query)
            reranked = self.reranker.rerank(query=query, documents=documents)
            strategy = "mqr_fallback"

        # Step 4 — Build prompt and generate answer
        messages = PromptBuilder.build(query=query, documents=reranked)
        response = self.llm.generate(messages=messages)

        return {
            "answer": response.content,
            "sources": self._extract_sources(reranked),
            "strategy": strategy,
        }

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    def _hybrid_retrieve(self, query: str) -> list[Document]:
        """Run hybrid retrieval (dense + BM25 + RRF)."""

        return self.hybrid_retriever.retrieve(
            query=query,
            top_k=self.top_k * 2,   # retrieve more before reranking
        )

    def _mqr_retrieve(self, query: str) -> list[Document]:
        """
        Run Multi-Query Retrieval.

        Generates multiple query variants, runs hybrid retrieval for
        each, and deduplicates by chunk_id before returning.
        """

        queries = self.mqr.generate_queries(question=query)

        seen: set[str] = set()
        all_documents: list[Document] = []

        for q in queries:
            results = self.hybrid_retriever.retrieve(
                query=q,
                top_k=self.top_k,
            )
            for doc in results:
                doc_id = (
                    doc.metadata.get("chunk_id")
                    or doc.metadata.get("id")
                    or hash(doc.page_content)
                )
                if doc_id not in seen:
                    seen.add(doc_id)
                    all_documents.append(doc)

        return all_documents

    # ------------------------------------------------------------------
    # Quality check
    # ------------------------------------------------------------------

    def _quality_ok(self, documents: list[Document]) -> bool:
        """
        Return True if the top reranked document meets the
        quality threshold.
        """

        if not documents:
            return False

        top_score = documents[0].metadata.get("reranker_score", 0.0)
        return float(top_score) >= QUALITY_THRESHOLD

    # ------------------------------------------------------------------
    # Source extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_sources(documents: list[Document]) -> list[dict]:
        """Extract source metadata from reranked documents."""

        sources = []

        for doc in documents:
            sources.append(
                {
                    "source": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "N/A"),
                    "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                    "reranker_score": round(
                        float(doc.metadata.get("reranker_score", 0.0)), 4
                    ),
                }
            )

        return sources
