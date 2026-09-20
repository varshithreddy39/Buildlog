from langchain_core.prompts import ChatPromptTemplate


evaluator_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an execution evaluator.

Evaluate whether the original user task has been completed.

Rules:
- completed=True only when the original task is fully satisfied.
- completed=False and continue_plan=True when the task is incomplete but the current plan is still valid.
- completed=False and continue_plan=False when the task is incomplete and the current plan is no longer sufficient.
- Consider failed task results when making the decision.
- Do not execute any task.
- Return only the structured evaluation."""
    ),
    (
        "human",
        """Original task:
{user_task}

Current plan:
{plan}

Execution results:
{results}"""
    )
])