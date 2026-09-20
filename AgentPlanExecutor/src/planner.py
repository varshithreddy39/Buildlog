from langchain_groq import ChatGroq

from config import GROQ_API_KEY
from src.schemas import Plan
from src.prompts.planner_prompt import planner_prompt


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY
)

planner_llm = llm.with_structured_output(Plan)

planner_chain = planner_prompt | planner_llm


def planner_node(state):

    plan = planner_chain.invoke({
        "user_task": state["user_task"],
        "plan_errors": state.get("plan_errors", [])
    })

    return {
        "plan": plan,
        "planner_attempts": state.get("planner_attempts", 0) + 1
    }