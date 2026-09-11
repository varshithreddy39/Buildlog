from pydantic import BaseModel, Field

from backend.config.settings import settings
from backend.rag.llm.llm import LLMManager
from backend.prompts.mqr_prompt import MQR_PROMPT


class QueryList(BaseModel):
    queries: list[str] = Field(
        description="List of generated search queries."
    )


class MultiQueryRetriever:
    def __init__(self) -> None:
        self.llm = LLMManager()
        self.config = settings.MQR_CONFIG

    def generate_queries(
        self,
        question: str,
    ) -> list[str]:

        messages = MQR_PROMPT.format_messages(
            question=question
        )

        response = self.llm.invoke(
            messages=messages,
            output_schema=QueryList,
        )

        expected_queries = self.config["num_queries"]

        if len(response.queries) != expected_queries:
            raise ValueError(
                f"Expected {expected_queries} queries, "
                f"but received {len(response.queries)}."
            )

        return response.queries