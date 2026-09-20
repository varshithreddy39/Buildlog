from langchain_groq import ChatGroq

from config import GROQ_API_KEY
from src.schemas import Plan
from src.prompts.replanner_prompt import replanner_prompt


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY
)

replanner_llm = llm.with_structured_output(Plan)

replanner_chain = replanner_prompt | replanner_llm


def replan(state):

    new_plan = replanner_chain.invoke({
        "user_task": state["user_task"],
        "plan": state["plan"],
        "results": state["results"],
        "evaluation": state["evaluation"]
    })

    return {
        "previous_plan": state["plan"],
        "plan": new_plan,
        "replan_attempts": state.get("replan_attempts", 0) + 1
    }