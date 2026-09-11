from langchain_core.documents import Document
from huggingface_hub import InferenceClient

from backend.config.settings import settings


class Reranker:
    """
    Reranks retrieved documents using a Hugging Face hosted
    cross-encoder reranker.
    """

    def __init__(self) -> None:
        self.config = settings.reranker_config

        self.model_name = self.config["MODEL_NAME"]
        self.top_k = self.config["TOP_K"]
        self.normalize_score = self.config["NORMALIZE_SCORE"]

        if not settings.HF_TOKEN:
            raise ValueError(
                "HF_TOKEN is not set in the environment variables."
            )

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=settings.HF_TOKEN,
        )

    def _score(
        self,
        query: str,
        document: str,
    ) -> float:
        """
        Get a relevance score from the hosted reranker.
        """

        response = self.client.post(
            json={
                "inputs": {
                    "text": query,
                    "text_pair": document,
                },
                "parameters": {
                    "function_to_apply": (
                        "sigmoid"
                        if self.normalize_score
                        else "none"
                    )
                },
            },
            model=self.model_name,
            task="text-classification",
        )

        result = response.json()

        if not isinstance(result, list) or not result:
            raise RuntimeError(
                f"Unexpected reranker response: {result}"
            )

        return float(result[0]["score"])

    def rerank(
        self,
        query: str,
        documents: list[Document],
    ) -> list[Document]:
        """
        Score and rerank retrieved documents.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if not documents:
            return []

        scored_documents = []

        for document in documents:
            score = self._score(
                query=query,
                document=document.page_content,
            )

            document.metadata["reranker_score"] = score

            scored_documents.append(document)

        scored_documents.sort(
            key=lambda document: document.metadata["reranker_score"],
            reverse=True,
        )

        return scored_documents[:self.top_k]