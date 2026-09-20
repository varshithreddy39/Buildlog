from src.schemas import ExecutionState


def reconcile_completed_tasks(state: ExecutionState):

    old_plan = state.get("previous_plan")
    new_plan = state.get("plan")

    old_completed = state.get("completed_tasks", set())
    old_results = state.get("results", {})

    if old_plan is None or new_plan is None:
        return {}

    old_tasks = {
        task.id: task
        for task in old_plan.tasks
    }

    new_tasks = {
        task.id: task
        for task in new_plan.tasks
    }

    preserved_tasks = set()
    preserved_results = {}

    for task_id in old_completed:

        if task_id not in old_tasks:
            continue

        if task_id not in new_tasks:
            continue

        old_task = old_tasks[task_id]
        new_task = new_tasks[task_id]

        if (
            old_task.name == new_task.name
            and old_task.description == new_task.description
            and old_task.capability == new_task.capability
            and old_task.depends_on == new_task.depends_on
        ):
            preserved_tasks.add(task_id)

            if task_id in old_results:
                preserved_results[task_id] = old_results[task_id]

    return {
        "completed_tasks": preserved_tasks,
        "results": preserved_results
    }