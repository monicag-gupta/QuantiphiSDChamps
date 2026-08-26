from typing import Annotated

from fastapi import APIRouter, Query, status

from src.api.dependencies import CurrentUser, DBSession
from src.api.schemas import (
    MemberCreate, MemberResponse, ProjectCreate, ProjectListResponse, ProjectPatch,
    ProjectResponse, ProjectStatus, ProjectSummaryResponse, TaskCreate, TaskListResponse, TaskResponse,
)
from src.service.project_service import ProjectService
from src.service.task_service import TaskService

router = APIRouter(prefix="/v1/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    db: DBSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: Annotated[ProjectStatus | None, Query(alias="status")] = None,
    manager_id: str | None = None,
):
    return ProjectService.list_projects(
        db, page=page, page_size=page_size,
        status=status_filter.value if status_filter else None,
        manager_id=manager_id,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: DBSession, current_user: CurrentUser):
    return ProjectService.create_project(db, payload, current_user)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: DBSession):
    return ProjectService.get_project(db, project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def patch_project(project_id: str, payload: ProjectPatch, db: DBSession, current_user: CurrentUser):
    return ProjectService.patch_project(db, project_id, payload, current_user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: DBSession, current_user: CurrentUser):
    ProjectService.delete_project(db, project_id, current_user)
    return None


@router.post("/{project_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(project_id: str, payload: MemberCreate, db: DBSession, current_user: CurrentUser):
    return ProjectService.add_member(db, project_id, payload, current_user)


@router.get("/{project_id}/tasks", response_model=TaskListResponse)
def list_tasks(project_id: str, db: DBSession):
    return TaskService.list_tasks(db, project_id)


@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(project_id: str, payload: TaskCreate, db: DBSession, current_user: CurrentUser):
    return TaskService.create_task(db, project_id, payload, current_user)


@router.get("/{project_id}/summary", response_model=ProjectSummaryResponse)
def get_summary(project_id: str, db: DBSession):
    return ProjectService.summary(db, project_id)
