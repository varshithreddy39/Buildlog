import re

import faiss 
import numpy as np
from rank_bm25 import BM25Okapi

def preprocess_text(text):

    text = text.lower()

    text = re.sub(r"[^\w\s]", "", text)

    return text.split()
def create_faiss_index(embeddings):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index



def search_faiss_index(
    index,
    query_embedding,
    k=5
):
    distances, indices = index.search(
        np.array([query_embedding]).astype("float32"),
        k
    )

    return distances, indices

def create_bm25_index(corpus):
    tokenized_corpus = [preprocess_text(doc) for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25

def search_bm25_index(bm25, query, k=5):
    tokenized_query = preprocess_text(query)
    scores = bm25.get_scores(tokenized_query)
    top_k_indices = np.argsort(scores)[::-1][:k]
    return top_k_indices, scores[top_k_indices]