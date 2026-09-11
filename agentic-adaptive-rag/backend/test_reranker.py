from backend.rag.embeddings import EmbeddingManager
from backend.rag.vector import VectorStoreManager
from backend.rag.retriever.vector import VectorRetriver
from backend.rag.retriever.reranker import Reranker


def main():

    query = "What are the main requirements of the project?"

    embedding_manager = EmbeddingManager()
    vector_store = VectorStoreManager()

    vector_retriever = VectorRetriver(
        embedding_manager=embedding_manager,
        vector_store=vector_store,
    )

    reranker = Reranker()

    documents = vector_retriever.retrive(
        query=query,
        top_k=5,
    )

    print("\n========== BEFORE RERANKING ==========\n")

    for i, document in enumerate(documents, start=1):
        print(f"Document {i}")
        print("Qdrant score:", document.metadata.get("score"))
        print("Chunk ID:", document.metadata.get("chunk_id"))
        print("Content:", document.page_content[:200])
        print()

    reranked_documents = reranker.rerank(
        query=query,
        documents=documents,
    )

    print("\n========== AFTER RERANKING ==========\n")

    for i, document in enumerate(reranked_documents, start=1):
        print(f"Document {i}")
        print("Qdrant score:", document.metadata.get("score"))
        print(
            "Reranker score:",
            document.metadata.get("reranker_score"),
        )
        print("Chunk ID:", document.metadata.get("chunk_id"))
        print("Content:", document.page_content[:200])
        print()


if __name__ == "__main__":
    main()