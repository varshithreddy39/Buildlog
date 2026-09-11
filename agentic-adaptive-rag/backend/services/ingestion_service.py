import hashlib
import uuid

from langchain_core.documents import Document
from qdrant_client.http.models import PointStruct

from backend.rag.loder import DocumentLoader
from backend.rag.splitter import DocumentSplitter
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vector import VectorStoreManager
from backend.rag.retriever.bm25 import SparseRetriever


class IngestionService:
    """
    Handles the complete document ingestion pipeline.

    Responsibilities:
        - Detect duplicate documents
        - Load documents
        - Split documents into chunks
        - Generate embeddings
        - Store embeddings in Qdrant
        - Build the BM25 index
    """

    def __init__(self) -> None:

        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter()
        self.embedding_manager = EmbeddingManager()
        self.vector_store = VectorStoreManager()
        self.sparse_retriever = SparseRetriever()

    def ingest(
        self,
        source: str,
    ) -> dict:
        """
        Ingest a document into the knowledge base.

        Args:
            source: Local file path or URL.

        Returns:
            Dictionary containing ingestion statistics.
        """

        file_hash = self._compute_file_hash(source)

        if self.vector_store.document_exists(file_hash):
            return {
                "status": "skipped",
                "message": "Document already exists.",
                "file_hash": file_hash,
            }

        documents = self.loader.load(source)

        chunks = self.splitter.split(documents)

        embeddings = self.embedding_manager.embed_documents(
            chunks
        )

        points = self._prepare_points(
            chunks=chunks,
            embeddings=embeddings,
            file_hash=file_hash,
        )

        self.vector_store.add_documents(points)

        self.sparse_retriever.build_index(chunks)

        return {
            "status": "success",
            "source": source,
            "file_hash": file_hash,
            "documents": len(documents),
            "chunks": len(chunks),
            "stored": len(points),
        }
    def _compute_file_hash(
    self,
    source: str,
    ) -> str:
        """
        Compute a SHA-256 hash for a local file or URL.

        For local files, the hash is generated from the file contents.
        For URLs, the hash is generated from the URL string.
        """

        if self.loader._is_url(source):
            return hashlib.sha256(
                source.encode("utf-8")
            ).hexdigest()

        sha256 = hashlib.sha256()

        with open(source, "rb") as file:
            while chunk := file.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    def _prepare_points(
    self,
    chunks: list[Document],
    embeddings: list[list[float]],
    file_hash: str,
   ) -> list[PointStruct]:
        """
        Convert document chunks and embeddings into
        Qdrant PointStruct objects.
        """

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must be equal."
            )

        points = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            point = PointStruct(
                id=self._generate_point_id(
                    chunk.metadata["chunk_id"]
                ),
                vector=embedding,
                payload=self._build_payload(
                    chunk,
                    file_hash,
                ),
            )

            points.append(point)

        return points
    def _build_payload(
    self,
    chunk: Document,
    file_hash: str,
    ) -> dict:
        """
        Build the payload stored alongside each vector
        in the Qdrant collection.
        """

        metadata = chunk.metadata

        return {
            "page_content": chunk.page_content,
            "source": metadata.get("source"),
            "document_type": metadata.get("document_type"),
            "page": metadata.get("page", 0),
            "chunk_id": metadata.get("chunk_id"),
            "chunk_index": metadata.get("chunk_index"),
            "chunk_size": metadata.get("chunk_size"),
            "file_hash": file_hash,
        }
    def _generate_point_id(
    self,
    chunk_id: str,
    ) -> str:
        """
        Generate a deterministic UUID for a document chunk.

        Using UUID5 ensures the same chunk always receives
        the same identifier across multiple ingestions.
        """

        return str(
            uuid.uuid5(
                uuid.NAMESPACE_DNS,
                chunk_id,
            )
        )
