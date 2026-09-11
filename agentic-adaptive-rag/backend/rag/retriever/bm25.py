from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

class SparseRetriever:
    def __init__(self):
        self.retriever = None

    def build_index(self, documents: list[Document]) -> None:
        self.retriever = BM25Retriever.from_documents(documents)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Document]:

        if self.retriever is None:
            raise RuntimeError("BM25 index not built.")

        self.retriever.k = top_k

        return self.retriever.invoke(query)