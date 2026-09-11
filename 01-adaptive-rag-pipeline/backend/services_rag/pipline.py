from services_rag.chunking import (extract_text_from_pdf,clean_text,langchain_chunking
)

from services_rag.llm import generate_answer

from services_rag.embeddings import generate_embeddings

from services_rag.vectorb import (create_faiss_index,search_faiss_index,create_bm25_index,search_bm25_index
)

from services_rag.reranker import rerank_chunks

from services_rag.mqr import generate_multi_query

from services_rag.query_rewriter import rewrite_query
from services_rag.memory import summarize_prompt

import re


store_chunks = []

faiss_index = None

bm25_index = None

chat_history = []

store_embeddings = []

conversation_summary = ""


def needs_query_rewrite(query):

    query = query.lower()

    ambiguous_patterns = [

        "it",
        "they",
        "them",
        "that",
        "those",
        "what about",
        "second",
        "first",
        "highest",
        "lowest",
        "this",
        "these",
        "he",
        "she",
        "him",
        "her"
    ]

    return any(
        pattern in query
        for pattern in ambiguous_patterns
    )


def handle_upload(
    file_content: bytes,
    filename: str,
) -> bool:

    global store_chunks
    global faiss_index
    global bm25_index
    global store_embeddings

    print(f"\nHandling upload for file: {filename}")

    raw_text = extract_text_from_pdf(file_content)

    print(raw_text[:3000])

    print(
        f"\nExtracted text length: {len(raw_text)}"
    )

    if not raw_text:

        return {
            "status": "error",
            "message": "No text extracted"
        }

    cleaned_text = clean_text(raw_text)

    chunks = langchain_chunking(cleaned_text)

    print(f"\nTotal Chunks Created: {len(chunks)}")

    if not chunks:

        return {
            "status": "error",
            "message": "No chunks processed"
        }
    for chunk in chunks:
        store_chunks.append({
        "chunks": chunk,
        "Source": filename
        })
    print("🔥 BEFORE EMBEDDINGS", flush=True)
    new_embeddings = generate_embeddings(chunks)
    print("🔥 AFTER EMBEDDINGS", flush=True)
    store_embeddings.extend(new_embeddings)

    print(
        f"\nComputed {len(new_embeddings)} embeddings"
    )

    if new_embeddings is None or len(new_embeddings) == 0:

        return {
            "status": "error",
            "message": "No embeddings generated"
        }

    if faiss_index is None:

        faiss_index = create_faiss_index(new_embeddings)
    else:
        
        faiss_index.add(new_embeddings)

    bm25_texts = [
    item["chunks"]
    for item in store_chunks
]

    bm25_index = create_bm25_index(
        bm25_texts
    )

    print("\nFAISS index created successfully")

    print(
        f"FAISS contains {faiss_index.ntotal} vectors"
    )
    print(f"Total Chunks: {len(store_chunks)}")
    print(f"Total Embeddings: {len(store_embeddings)}")
    print(f"FAISS vectors: {faiss_index.ntotal}")

    return {
        "status": "success",
        "message": "PDF processed successfully",
        "total_chunks": len(chunks)
    }


def question_answer_pipeline(query):

    global store_chunks
    global faiss_index
    global bm25_index
    global chat_history
    global conversation_summary

    print("\n=================================================")
    print("NEW QUESTION RECEIVED")
    print("=================================================")

    print(f"\nOriginal User Query: {query}")

    if not store_chunks or faiss_index is None:

        return {
            "status": "error",
            "message": "No PDF processed yet"
        }

    original_query = query
    evaluation_mode = False

    if not evaluation_mode and needs_query_rewrite(query):

        print("\nQuery rewriting triggered")

        rewritten_query = rewrite_query(
            query=query,
            history=chat_history,
            summary=conversation_summary
        )

        print(f"\nRewritten Query: {rewritten_query}")

        query = rewritten_query

    else:

        print("\nQuery rewriting NOT triggered")

    total_chunks = len(store_chunks)

    if total_chunks <= 5:

        k = 2

    elif total_chunks <= 10:

        k = 3

    else:

        k = 5

    print(f"\nDynamic K selected: {k}")

    query_embedding = generate_embeddings([query])[0]

    print("\nQuery embedding generated")

    distances, indices = search_faiss_index(
        faiss_index,
        query_embedding,
        k=k
    )

    top_k_indices, bm25_scores = search_bm25_index(
        bm25_index,
        query,
        k=k
    )

    print("\nFAISS Retrieval Indices:")
    print(indices[0])

    print("\nBM25 Retrieval Indices:")
    print(top_k_indices)

    combined_indices = [

        idx

        for idx in dict.fromkeys(

            list(indices[0]) + list(top_k_indices)

        )

        if idx != -1
    ]

    print("\nHybrid Retrieval Indices:")
    print(combined_indices)

    all_indices = combined_indices.copy()

    top_distance = distances[0][0]

    top_bm25_score = bm25_scores[0]

    print(f"\nTop FAISS Distance: {top_distance:.4f}")

    print(f"Top BM25 Score: {top_bm25_score:.4f}")

    faiss_threshold = 1.0

    bm25_threshold = 0.5

    if (
        top_distance > faiss_threshold
        and top_bm25_score < bm25_threshold
    ):

        print("\nMQR triggered")

        expanded_queries = generate_multi_query(query)

        for eq in expanded_queries:

            print(f"\nExpanded Query: {eq}")

            eq_embedding = generate_embeddings([eq])[0]

            eq_distances, eq_indices = search_faiss_index(
                faiss_index,
                eq_embedding,
                k=k
            )

            eq_top_k_indices, eq_bm25_scores = (
                search_bm25_index(
                    bm25_index,
                    eq,
                    k=k
                )
            )

            combined_eq_indices = [

                idx

                for idx in dict.fromkeys(

                    list(eq_indices[0])
                    +
                    list(eq_top_k_indices)

                )

                if idx != -1
            ]

            print(
                f"Expanded Query Retrieval Indices: "
                f"{combined_eq_indices}"
            )

            all_indices.extend(combined_eq_indices)

    else:

        print("\nMQR NOT triggered")

    all_indices = list(dict.fromkeys(all_indices))

    print("\nFinal Retrieval Indices:")
    print(all_indices)

    retrieved_chunks = [

        store_chunks[idx]['chunks']

        for idx in all_indices

        if idx != -1
    ]
    sources = list(set(

        store_chunks[idx]['Source']

        for idx in all_indices

        if idx != -1
    ))

    print("\nRetrieved Chunks:")

    for i, chunk in enumerate(retrieved_chunks):

        print(
            f"\nChunk {i+1} "
            f"(Index: {all_indices[i]}):\n"
        )

        print(chunk)

    reranked_chunks = rerank_chunks(
        query,
        retrieved_chunks,
        top_k=min(2, len(retrieved_chunks))
    )

    print("\nReranked Chunks:")

    for i, (chunk, score) in enumerate(reranked_chunks):

        print(
            f"\nChunk {i+1} "
            f"(Score: {score:.4f})"
        )

        print(chunk)

    final_chunks = [

        chunk

        for chunk, score in reranked_chunks
    ]

    answer = generate_answer(

        query=query,

        chunks=final_chunks,

        history=chat_history,
        summary=conversation_summary
    )

    print("\nGenerated Answer:")
    print(answer)

    chat_history.append({

        "user": original_query,

        "assistant": answer
    })

    print("\nChat History Updated")

    print(f"Total Conversation Turns: {len(chat_history)}")

    if len(chat_history) >= 8:

        conversation_summary = summarize_prompt(old_summary=conversation_summary, chat_history=chat_history)

        print("\nConversation Summary Updated")
        print(conversation_summary)
        chat_history = chat_history[-3:]
    


    return {
        "answer": answer,
        "contexts": final_chunks,
        "sources": sources
    }