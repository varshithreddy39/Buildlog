from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

from rag.prompts.system_prompt import SYSTEM_PROMPT


class PromptBuilder:
    """
    Builds the final ChatPromptTemplate for the RAG pipeline.
    """

    @staticmethod
    def _format_context(documents: List[Document]) -> str:
        """
        Convert retrieved documents into a readable context block.
        """

        if not documents:
            return "No relevant context was retrieved."

        formatted_chunks = []

        for index, document in enumerate(documents, start=1):

            source = document.metadata.get("source", "Unknown")
            page = document.metadata.get("page", "N/A")

            formatted_chunks.append(
                f"""
### Context {index}

Source: {source}
Page: {page}

{document.page_content.strip()}
"""
            )

        return "\n\n".join(formatted_chunks)

    @classmethod
    def build(
        cls,
        query: str,
        documents: List[Document],
    ):
        """
        Build the final prompt messages for the LLM.
        """

        context = cls._format_context(documents)

        prompt = ChatPromptTemplate.from_messages(
            [
                SYSTEM_PROMPT,
                HumanMessagePromptTemplate.from_template(
                    """
Use the following retrieved context to answer the user's question.

<context>

{context}

</context>

Question:
{question}
"""
                ),
            ]
        )

        return prompt.format_messages(
            context=context,
            question=query,
        )