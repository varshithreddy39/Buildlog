import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN")
)

MODEL_NAME = "BAAI/bge-reranker-v2-m3"


def rerank_chunks(query, chunks, top_k=3):

    if not chunks:
        return []

    scored_chunks = []

    for chunk in chunks:

        text = f"Query: {query}\nDocument: {chunk}"

        result = client.text_classification(
            text,
            model=MODEL_NAME,
            top_k=1
        )

        score = result[0]["score"]

        scored_chunks.append(
            (chunk, score)
        )

    scored_chunks.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return scored_chunks[:top_k]