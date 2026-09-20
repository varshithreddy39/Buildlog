from src.graph import app


initial_state = {
    "user_task": "Create a Python data processing pipeline that reads a CSV file, cleans missing values, calculates summary statistics, and generates a final report.",

    "plan": None,
    "previous_plan": None,

    "runtime_tasks": [],
    "results": {},
    "evaluation": None,
    "completed_tasks": set(),
    "ready_tasks": [],

    "plan_errors": [],
    "planner_attempts": 0,
    "replan_attempts":0
}


print("Starting full graph...\n")

final_state = app.invoke(initial_state)


print("\n========== FINAL STATE ==========\n")

print("Planner attempts:")
print(final_state["planner_attempts"])

print("\nPlan:")
for task in final_state["plan"].tasks:
    print(f"- {task.id}: {task.name}")
    print(f"  Depends on: {task.depends_on}")

print("\nPlan errors:")
print(final_state["plan_errors"])

print("\nEvaluation:")
print(final_state["evaluation"])

print("\nResults:")
for task_id, result in final_state["results"].items():
    print(f"{task_id}: {result}")