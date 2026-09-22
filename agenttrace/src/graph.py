from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from src.memory.checkpointer import checkpointer
from src.state import AgentState
from src.nodes.chatbot import chatbot
from src.tools import multiply, web_search


tools = [multiply, web_search]

builder = StateGraph(AgentState)

builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")

builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

builder.add_edge("tools", "chatbot")

graph = builder.compile(checkpointer=checkpointer)