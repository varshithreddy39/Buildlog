import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
   

    # ==========================================================
    # API KEYS
    # ==========================================================
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    HF_TOKEN = os.getenv("HF_TOKEN")

    # ==========================================================
    # MODELS
    # ==========================================================
    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "qwen/qwen3-30b-a3b:free"
    )

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "BAAI/bge-small-en-v1.5"
    )

    # ==========================================================
    # LLM CONFIGURATION
    # ==========================================================
    LLM_CONFIG = {
        "provider": "openrouter",
        "model": LLM_MODEL,

        # Generation Parameters
        "temperature": 0.2,
        "max_tokens": 1024,
        "top_p": 0.95,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,

        # Runtime
        "stream": False,
        "timeout": 60,
        "max_retries": 3,

        # Context Window
        "context_window": 32768,
    }

    # ==========================================================
    # EMBEDDING CONFIGURATION
    # ==========================================================
    EMBEDDING_CONFIG = {
        "provider": "huggingface",
        "model_name": EMBEDDING_MODEL,
        "encode_kwargs": {
            "normalize_embeddings": True,
        },
        "model_kwargs": {
            "device": "cpu",
        },
    }

    # ==========================================================
    # DOCUMENT CHUNKING
    # ==========================================================
    CHUNKING_CONFIG = {

        "pdf": {
            "strategy": "recursive",
            "chunk_size": 1200,
            "chunk_overlap": 200,
            "separators": [
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ],
        },

        "docx": {
            "strategy": "recursive",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "separators": [
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ],
        },

        "csv": {
            "strategy": "csv",
        },

        "web": {
            "strategy": "recursive",
            "chunk_size": 800,
            "chunk_overlap": 150,
            "separators": [
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ],
        },
    }

    # ==========================================================
    # QDRANT CONFIGURATION
    # ==========================================================
    QDRANT_CONFIG = {
        "host": os.getenv("QDRANT_HOST", "localhost"),
        "port": int(os.getenv("QDRANT_PORT", 6333)),
        "collection_name": "knowledge_base",

        # Vector Configuration
        "vector_size": 384,
        "distance": "cosine",

        # HNSW Configuration
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100,
        },

        # Optimizer Configuration
        "optimizer_config": {
            "indexing_threshold": 20000,
        },

        # Storage
        "on_disk_payload": True,

        # Quantization
        "quantization": None,
    }

    # ==========================================================
    # MULTI QUERY RETRIEVER (MQR)
    # ==========================================================
    MQR_CONFIG = {
        "num_queries": 4,
        "include_original_query": True,
        "temperature": 0.3,
        "max_tokens": 150,
    }

    # ==========================================================
    # API CONFIGURATION
    # ==========================================================
    API_CONFIG = {
        "timeout": 60,
        "retry_attempts": 3,
        "retry_delay": 2,
    }

    reranker_config = {
    "MODEL_NAME": "BAAI/bge-reranker-v2-m3",
    "DEVICE": "cpu",              
    "TOP_K": 5,
    "BATCH_SIZE": 16,
    "MAX_LENGTH": 1024,
    "NORMALIZE_SCORE": True,
    "RETURN_SCORE": True
}

    

settings = Settings()