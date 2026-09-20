from concurrent.futures import ThreadPoolExecutor, as_completed

from src.schemas import RuntimeTask


def execute_task(task: RuntimeTask) -> str:

    if task.capability == "llm":
        return f"Executed task: {task.name}"

    raise ValueError(
        f"Unsupported capability: {task.capability}"
    )


def execute_ready_tasks(
    tasks: list[RuntimeTask]
) -> dict[str, str]:

    if not tasks:
        return {}

    results = {}

    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:

        futures = {
            executor.submit(execute_task, task): task
            for task in tasks
        }

        for future in as_completed(futures):

            task = futures[future]

            try:
                result = future.result()

                # Use stable logical task ID
                results[task.task_id] = result

            except Exception as error:

                results[task.task_id] = f"ERROR: {error}"

    return results