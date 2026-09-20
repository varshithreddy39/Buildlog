from langgraph.graph import StateGraph, START, END

from src.schemas import ExecutionState
from src.planner import planner_node
from src.validator import validate_plan
from src.runtime import create_runtime_tasks
from src.scheduler import get_ready_tasks
from src.executor import execute_ready_tasks
from src.evaluator import evaluate_execution
from src.replanner import replan
from src.reconciler import reconcile_completed_tasks


MAX_PLANNER_ATTEMPTS = 3

graph = StateGraph(ExecutionState)




graph.add_node("planner", planner_node)
graph.add_edge(START, "planner")



graph.add_node("validator", validate_plan)
graph.add_edge("planner", "validator")


def route_after_validation(state):

    if not state["plan_errors"]:
        return "valid"

    if state["planner_attempts"] < MAX_PLANNER_ATTEMPTS:
        return "retry"

    return "failed"


graph.add_conditional_edges(
    "validator",
    route_after_validation,
    {
        "valid": "runtime",
        "retry": "planner",
        "failed": END
    }
)




graph.add_node("runtime", create_runtime_tasks)
graph.add_edge("runtime", "scheduler")




def scheduler_node(state):

    ready_tasks = get_ready_tasks(
        state["runtime_tasks"],
        state.get("completed_tasks", set())
    )

    return {
        "ready_tasks": ready_tasks
    }


graph.add_node("scheduler", scheduler_node)


def route_after_scheduler(state):

    ready_tasks = state["ready_tasks"]

    if ready_tasks:
        return "execute"

    completed = state.get("completed_tasks", set())
    total_tasks = state["runtime_tasks"]

    if len(completed) == len(total_tasks):
        return "evaluate"

    return "replan"


graph.add_conditional_edges(
    "scheduler",
    route_after_scheduler,
    {
        "execute": "executor",
        "evaluate": "evaluator",
        "replan": "replanner"
    }
)


def executor_node(state):

    batch_results = execute_ready_tasks(
        state["ready_tasks"]
    )

    new_completed_tasks = {
        task_id
        for task_id, result in batch_results.items()
        if not result.startswith("ERROR:")
    }

    completed_tasks = (
        state.get("completed_tasks", set())
        | new_completed_tasks
    )

    all_results = {
        **state.get("results", {}),
        **batch_results
    }

    return {
        "results": all_results,
        "completed_tasks": completed_tasks
    }


graph.add_node("executor", executor_node)
graph.add_edge("executor", "evaluator")




graph.add_node("evaluator", evaluate_execution)


def route_after_evaluation(state):

    evaluation = state["evaluation"]

    if evaluation.completed:
        return "finish"

    if evaluation.continue_plan:

        
        if state.get("ready_tasks"):
            return "continue"

        
        return "replan"

    return "replan"


graph.add_conditional_edges(
    "evaluator",
    route_after_evaluation,
    {
        "finish": END,
        "continue": "scheduler",
        "replan": "replanner"
    }
)



graph.add_node("replanner", replan)
graph.add_edge("replanner", "reconciler")

graph.add_node("reconciler", reconcile_completed_tasks)
graph.add_edge("reconciler", "validator")


app = graph.compile()