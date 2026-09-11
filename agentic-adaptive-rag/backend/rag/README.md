# backend/rag

This module contains the full Adaptive RAG pipeline used by the RAG Agent.

## Module Map

| File | Responsibility |
|---|---|
| `loder.py` | Document loading — PDF, DOCX, CSV, Web URLs |
| `splitter.py` | Type-aware chunking with metadata enrichment |
| `embeddings.py` | HuggingFace embedding manager (`BAAI/bge-small-en-v1.5`) |
| `vector.py` | Qdrant vector store — create, upsert, search, dedup |
| `pipline.py` | End-to-end RAG query pipeline |
| `llm/llm.py` | LLM manager via OpenRouter (`Qwen3-30B`) |
| `retriever/vector.py` | Dense vector retriever |
| `retriever/bm25.py` | BM25 sparse retriever |
| `retriever/hybrid.py` | Hybrid retriever with RRF fusion |
| `retriever/mqr.py` | Multi-query retriever (4 query variants) |
| `retriever/reranker.py` | Cross-encoder reranker (`BAAI/bge-reranker-v2-m3`) |
| `prompts/system_prompt.py` | System-level LLM behavior instructions |
| `prompts/mqr_prompt.py` | Prompt template for MQR query generation |
| `prompts/prompt_builder.py` | Builds final RAG prompt with context injection |

## Pipeline Flow

```
Query
  ↓
Hybrid Retrieval (Dense + BM25 → RRF)
  ↓
Cross-Encoder Reranker
  ↓
Quality Check (score ≥ 0.4)
  ↓ (fail → MQR → back to Hybrid)
LLM Generation
  ↓
Answer + Sources
```
