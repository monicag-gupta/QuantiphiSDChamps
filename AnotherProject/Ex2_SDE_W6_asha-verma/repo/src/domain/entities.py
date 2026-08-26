from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


ALLOWED_TASK_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.BLOCKED, TaskStatus.DONE, TaskStatus.CANCELLED},
    TaskStatus.BLOCKED: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.DONE: {TaskStatus.IN_PROGRESS},
    TaskStatus.CANCELLED: {TaskStatus.TODO},
}


@dataclass(slots=True)
class Task:
    task_id: str
    title: str
    status: TaskStatus = TaskStatus.TODO
    due_date: date | None = None
    estimate_hours: float | None = None

    def transition_to(self, new_status: TaskStatus) -> None:
        if new_status == self.status:
            return
        if new_status not in ALLOWED_TASK_TRANSITIONS[self.status]:
            raise ValueError(f"Illegal task transition: {self.status} -> {new_status}")
        self.status = new_status


@dataclass(slots=True)
class Project:
    project_id: str
    name: str
    start_date: date
    end_date: date
    status: ProjectStatus = ProjectStatus.PLANNED
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("Project end_date cannot be before start_date")

    def validate_task_due_date(self, due_date: date | None) -> None:
        if due_date is None:
            return
        if not (self.start_date <= due_date <= self.end_date):
            raise ValueError("Task due_date must fall within project dates")

    @property
    def completion_percentage(self) -> float:
        if not self.tasks:
            return 0.0
        completed = sum(1 for task in self.tasks if task.status == TaskStatus.DONE)
        return round((completed / len(self.tasks)) * 100, 2)


@dataclass(slots=True)
class Risk:
    risk_id: str
    title: str
    probability: int
    impact: int

    def __post_init__(self) -> None:
        if not 1 <= self.probability <= 5:
            raise ValueError("probability must be between 1 and 5")
        if not 1 <= self.impact <= 5:
            raise ValueError("impact must be between 1 and 5")

    @property
    def score(self) -> int:
        return self.probability * self.impact
