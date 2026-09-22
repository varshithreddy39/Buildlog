from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper

from src.schemas import WebSearchInput


search = SerpAPIWrapper()


@tool(args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """Search the web for current information."""
    return search.run(query)


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b