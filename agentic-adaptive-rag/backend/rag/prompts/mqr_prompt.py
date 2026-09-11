from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

MQR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert search query generation assistant.

Your task is to rewrite a user's question into multiple diverse search queries
that improve document retrieval for a Retrieval-Augmented Generation (RAG) system.

Rules:
- Preserve the original meaning.
- Generate 4 unique search queries.
- Each query should focus on a different perspective.
- Do not answer the question.
- Do not explain your reasoning.
- Return only the requested JSON format.

Output Format:
{
    "queries": [
        "...",
        "...",
        "...",
        "..."
    ]
}
"""
        ),
        (
            "human",
            "{question}"
        ),
    ]
)