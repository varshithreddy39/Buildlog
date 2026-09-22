from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    """Input schema for the web search tool."""

    query: str = Field(
        description="The search query to send to the web search API."
    )