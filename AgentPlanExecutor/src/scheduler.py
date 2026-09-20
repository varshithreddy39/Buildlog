from src.schemas import RuntimeTask


def get_ready_tasks(
    runtime_tasks: list[RuntimeTask],
    completed_tasks: set[str]
) -> list[RuntimeTask]:

    ready_tasks = []

    for task in runtime_tasks:

        # Already completed
        if task.task_id in completed_tasks:
            continue

        # All logical dependencies are completed
        if all(
            dependency in completed_tasks
            for dependency in task.dependencies
        ):
            ready_tasks.append(task)

    return ready_tasks