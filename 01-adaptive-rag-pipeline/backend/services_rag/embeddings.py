import os
import numpy as np
from huggingface_hub import InferenceClient


client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN")
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def generate_embeddings(data):

    embeddings = []

    for text in data:

        embedding = client.feature_extraction(
            text,
            model=MODEL_NAME
        )

        embedding = np.asarray(
            embedding,
            dtype="float32"
        )

        if embedding.ndim > 1:
            embedding = embedding.mean(axis=0)

        embeddings.append(embedding)

    return np.asarray(
        embeddings,
        dtype="float32"
    )