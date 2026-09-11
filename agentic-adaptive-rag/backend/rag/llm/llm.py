from typing import Type

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from backend.config.settings import settings


class LLMManager:
    """
    Wrapper around the configured LangChain chat model.

    This class provides a single interface for interacting with the LLM
    throughout the application.
    """

    def __init__(self) -> None:
        """Initialize the configured LLM client."""

        config = settings.LLM_CONFIG

        if not settings.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not set in the environment variables."
            )

        self.client = ChatOpenAI(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            timeout=config["timeout"],
            max_retries=config["max_retries"],
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    @property
    def model_name(self) -> str:
        """Return the configured model name."""

        return settings.LLM_CONFIG["model"]

    def generate(
        self,
        messages: list[BaseMessage],
        output_schema: Type[BaseModel] | None = None,
    ) -> AIMessage | BaseModel:
        """
        Generate a response from the LLM.

        Args:
            messages:
                List of LangChain messages.

            output_schema:
                Optional Pydantic model for structured outputs.

        Returns:
            AIMessage:
                Standard chat response.

            BaseModel:
                Structured response when output_schema is provided.
        """

        if output_schema is not None:
            structured_client = self.client.with_structured_output(
                output_schema
            )
            return structured_client.invoke(messages)

        response = self.client.invoke(messages)

        return self._validate_response(response)

    @staticmethod
    def _validate_response(
        response: AIMessage,
    ) -> AIMessage:
        """
        Validate the response returned by the LLM.

        Args:
            response:
                Response returned by the LangChain chat model.

        Returns:
            Validated AIMessage.

        Raises:
            ValueError:
                If the response is empty.

            TypeError:
                If the response is not an AIMessage.
        """

        if response is None:
            raise ValueError("LLM returned no response.")

        if not isinstance(response, AIMessage):
            raise TypeError(
                f"Expected AIMessage, got {type(response).__name__}."
            )

        if not response.content:
            raise ValueError("LLM returned an empty response.")

        if (
            isinstance(response.content, str)
            and not response.content.strip()
        ):
            raise ValueError("LLM returned an empty response.")

        return response