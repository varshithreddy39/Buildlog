from src.prompts import SYSTEM_PROMPT
from src.state import AgentState
from src.models import llm_with_tools


def chatbot(state: AgentState):
    messages = state["messages"]

    response = llm_with_tools.invoke(
        [
            ("system", SYSTEM_PROMPT),
            *messages,
        ]
    )

    return {
        "messages": [response]
    }