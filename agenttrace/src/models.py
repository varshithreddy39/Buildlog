import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.tools import multiply, web_search


load_dotenv()


llm = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
)

tools = [multiply, web_search]

llm_with_tools = llm.bind_tools(tools)