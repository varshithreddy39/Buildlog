from pydantic import BaseModel, Field
from typing import Literal, TypedDict
from uuid import UUID, uuid4


class PlannedTask(BaseModel):
    id: str = Field(
        description="Short unique task ID, such as task_1 or task_2."
    )
    name: str
    description: str
    capability: Literal["llm"] = "llm"
    depends_on: list[str] = Field(default_factory=list)


class Plan(BaseModel):
    tasks: list[PlannedTask]


class RuntimeTask(BaseModel):
    id: UUID = Field(default_factory=uuid4)


    task_id: str

    name: str
    description: str
    capability: str
    dependencies: list[str] = Field(default_factory=list)


class Evaluation(BaseModel):
    completed: bool = Field(
        description="Whether the original user task has been fully completed."
    )
    continue_plan: bool = Field(
        description="Whether the current plan is still valid and execution should continue."
    )
    reason: str = Field(
        description="Explain why the task is complete, should continue, or needs replanning."
    )


class ExecutionState(TypedDict):
    user_task: str

    plan: Plan | None
    previous_plan: Plan | None

    runtime_tasks: list[RuntimeTask]
    results: dict[str, str]
    evaluation: Evaluation | None
    completed_tasks: set[str]
    ready_tasks: list[RuntimeTask]

    plan_errors: list[str]
    planner_attempts: int
    replan_attempts: int