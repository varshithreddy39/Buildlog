from uuid import uuid4

from src.schemas import ExecutionState, RuntimeTask


def create_runtime_tasks(state: ExecutionState):

    plan = state["plan"]

    id_to_runtime_id = {}

    for task in plan.tasks:
        id_to_runtime_id[task.id] = uuid4()

    runtime_tasks = []

    for task in plan.tasks:

        runtime_task = RuntimeTask(
            id=id_to_runtime_id[task.id],
            task_id=task.id,
            name=task.name,
            description=task.description,
            capability=task.capability,
            dependencies=task.depends_on
        )

        runtime_tasks.append(runtime_task)

    return {
        "runtime_tasks": runtime_tasks
    }