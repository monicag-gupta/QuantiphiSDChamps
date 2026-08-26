from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MemberRole(StrEnum):
    MANAGER = "manager"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProjectCreate(StrictModel):
    name: str = Field(min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date
    end_date: date
    status: ProjectStatus = ProjectStatus.PLANNED

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class ProjectPatch(StrictModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None
    end_date: date | None = None
    status: ProjectStatus | None = None

    @model_validator(mode="after")
    def reject_empty_and_nulls(self):
        supplied = self.model_fields_set
        if not supplied:
            raise ValueError("PATCH body must contain at least one field")
        for field in supplied:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    manager_id: str
    status: ProjectStatus
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int


class MemberCreate(StrictModel):
    user_id: str = Field(min_length=36, max_length=36)
    role: MemberRole = MemberRole.CONTRIBUTOR


class MemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: MemberRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(StrictModel):
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    milestone_id: str | None = Field(default=None, min_length=36, max_length=36)
    assignee_id: str | None = Field(default=None, min_length=36, max_length=36)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None
    estimate_hours: float | None = Field(default=None, gt=0, le=10000)


class TaskPatch(StrictModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    milestone_id: str | None = Field(default=None, min_length=36, max_length=36)
    assignee_id: str | None = Field(default=None, min_length=36, max_length=36)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    estimate_hours: float | None = Field(default=None, gt=0, le=10000)

    @model_validator(mode="after")
    def reject_empty_and_nulls(self):
        supplied = self.model_fields_set
        if not supplied:
            raise ValueError("PATCH body must contain at least one field")
        for field in supplied:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TaskResponse(BaseModel):
    id: str
    project_id: str
    milestone_id: str | None
    title: str
    description: str | None
    assignee_id: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    estimate_hours: float | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int


class ProjectSummaryResponse(BaseModel):
    project_id: str
    total_tasks: int
    completed_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    completion_percentage: float
    open_risks: int
    total_logged_hours: float
