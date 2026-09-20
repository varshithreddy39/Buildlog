from langchain_openrouter import ChatOpenRouter
from langchain_groq import ChatGroq
from src.schemas import Evaluation
from src.prompts.evaluator_prompt import evaluator_prompt
from config import OPENROUTER_API_KEY,GROQ_API_KEY

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY
)

evaluator_llm = llm.with_structured_output(Evaluation)

evaluator_chain = evaluator_prompt | evaluator_llm


def evaluate_execution(state):

    evaluation = evaluator_chain.invoke({
        "user_task": state["user_task"],
        "plan": state["plan"],
        "results": state["results"]
    })

    return {
        "evaluation": evaluation
    }