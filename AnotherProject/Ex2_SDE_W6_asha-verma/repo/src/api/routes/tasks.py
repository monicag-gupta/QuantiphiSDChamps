from fastapi import APIRouter, status

from src.api.dependencies import CurrentUser, DBSession
from src.api.schemas import TaskPatch, TaskResponse
from src.service.task_service import TaskService

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: DBSession):
    return TaskService.get_task(db, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task(task_id: str, payload: TaskPatch, db: DBSession, current_user: CurrentUser):
    return TaskService.patch_task(db, task_id, payload, current_user)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: DBSession, current_user: CurrentUser):
    TaskService.delete_task(db, task_id, current_user)
    return None
