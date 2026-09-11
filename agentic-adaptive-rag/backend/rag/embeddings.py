from backend.config.settings import settings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingManager:

    def __init__(self) -> None:

        self.embedding_config = settings.EMBEDDING_CONFIG

        self._embedding_model = self._load_embedding_model()

    def _load_embedding_model(self) -> HuggingFaceEmbeddings:

        return HuggingFaceEmbeddings(
            model_name=self.embedding_config["model_name"],
            encode_kwargs=self.embedding_config["encode_kwargs"],
            model_kwargs=self.embedding_config["model_kwargs"],
        )
           

    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[list[float]]:

        texts = [doc.page_content for doc in documents]
        return self._embedding_model.embed_documents(texts)

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        
        return self._embedding_model.embed_query(query)

        