from src.schemas import Plan


def has_cycle(plan: Plan):
    dependencies = {
        task.id: task.depends_on
        for task in plan.tasks
    }

    visiting = set()
    visited = set()

    def dfs(task_id):

        if task_id in visiting:
            return True

        if task_id in visited:
            return False

        visiting.add(task_id)

        for dependency in dependencies[task_id]:
            if dfs(dependency):
                return True

        visiting.remove(task_id)
        visited.add(task_id)

        return False

    for task_id in dependencies:
        if dfs(task_id):
            return True

    return False


def validate_plan(state):

    plan = state["plan"]
    errors = []

    task_ids = [task.id for task in plan.tasks]

    # Duplicate IDs
    if len(task_ids) != len(set(task_ids)):
        errors.append("Task IDs must be unique.")

    task_id_set = set(task_ids)

    # Validate dependencies
    for task in plan.tasks:

        for dependency in task.depends_on:

            if dependency not in task_id_set:
                errors.append(
                    f"Task '{task.id}' depends on unknown task '{dependency}'."
                )

        if task.id in task.depends_on:
            errors.append(
                f"Task '{task.id}' cannot depend on itself."
            )

    # Cycle detection
    if not errors and has_cycle(plan):
        errors.append(
            "Plan contains a dependency cycle."
        )

    return {
        "plan_errors": errors
    }