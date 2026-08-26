from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import TaskCreate, TaskPatch
from src.domain.entities import ALLOWED_TASK_TRANSITIONS, TaskStatus as DomainTaskStatus
from src.models.orm import ActivityLog, Milestone, Project, Task, User
from src.repository.activity_repository import ActivityRepository
from src.repository.project_repository import ProjectRepository
from src.repository.task_repository import TaskRepository


class TaskService:
    @staticmethod
    def _require_project(db: Session, project_id: str) -> Project:
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @staticmethod
    def _require_task(db: Session, task_id: str) -> Task:
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @staticmethod
    def _require_member(db: Session, project_id: str, user_id: str):
        member = ProjectRepository.get_member(db, project_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Project membership required")
        return member

    @staticmethod
    def _validate_due_date(project: Project, due_date):
        if due_date is not None and not (project.start_date <= due_date <= project.end_date):
            raise HTTPException(status_code=422, detail="Task due_date must fall within project dates")

    @staticmethod
    def _validate_assignee(db: Session, project_id: str, assignee_id: str | None):
        if assignee_id and not ProjectRepository.get_member(db, project_id, assignee_id):
            raise HTTPException(status_code=422, detail="Task assignee must be a project member")

    @staticmethod
    def _validate_milestone(db: Session, project_id: str, milestone_id: str | None):
        if not milestone_id:
            return
        milestone = db.get(Milestone, milestone_id)
        if not milestone or milestone.project_id != project_id:
            raise HTTPException(status_code=422, detail="Milestone must belong to the project")

    @classmethod
    def list_tasks(cls, db: Session, project_id: str):
        cls._require_project(db, project_id)
        items, total = TaskRepository.list_for_project(db, project_id)
        return {"items": items, "total": total}

    @classmethod
    def create_task(cls, db: Session, project_id: str, payload: TaskCreate, actor: User) -> Task:
        project = cls._require_project(db, project_id)
        cls._require_member(db, project_id, actor.id)
        cls._validate_due_date(project, payload.due_date)
        cls._validate_assignee(db, project_id, payload.assignee_id)
        cls._validate_milestone(db, project_id, payload.milestone_id)
        task = Task(
            id=str(uuid4()), project_id=project_id, milestone_id=payload.milestone_id,
            title=payload.title, description=payload.description, assignee_id=payload.assignee_id,
            status=payload.status.value, priority=payload.priority.value,
            due_date=payload.due_date, estimate_hours=payload.estimate_hours,
        )
        TaskRepository.add(db, task)
        ActivityRepository.add(db, ActivityLog(
            id=str(uuid4()), project_id=project_id, actor_id=actor.id,
            action="task.created", entity_type="task", entity_id=task.id,
            details=task.title,
        ))
        db.commit()
        db.refresh(task)
        return task

    @classmethod
    def get_task(cls, db: Session, task_id: str) -> Task:
        return cls._require_task(db, task_id)

    @classmethod
    def patch_task(cls, db: Session, task_id: str, payload: TaskPatch, actor: User) -> Task:
        task = cls._require_task(db, task_id)
        project = cls._require_project(db, task.project_id)
        if actor.id not in {project.manager_id, task.assignee_id}:
            raise HTTPException(status_code=403, detail="Only the project manager or current assignee may update this task")
        changes = payload.model_dump(exclude_unset=True)
        if "status" in changes:
            current = DomainTaskStatus(task.status)
            target = DomainTaskStatus(changes["status"].value)
            if target != current and target not in ALLOWED_TASK_TRANSITIONS[current]:
                raise HTTPException(status_code=409, detail=f"Illegal task transition: {current.value} -> {target.value}")
        if "due_date" in changes:
            cls._validate_due_date(project, changes["due_date"])
        if "assignee_id" in changes:
            cls._validate_assignee(db, project.id, changes["assignee_id"])
        if "milestone_id" in changes:
            cls._validate_milestone(db, project.id, changes["milestone_id"])
        for key, value in changes.items():
            if key in {"status", "priority"}:
                value = value.value
            setattr(task, key, value)
        ActivityRepository.add(db, ActivityLog(
            id=str(uuid4()), project_id=project.id, actor_id=actor.id,
            action="task.updated", entity_type="task", entity_id=task.id,
            details=",".join(sorted(changes.keys())),
        ))
        db.commit()
        db.refresh(task)
        return task

    @classmethod
    def delete_task(cls, db: Session, task_id: str, actor: User) -> None:
        task = cls._require_task(db, task_id)
        project = cls._require_project(db, task.project_id)
        if actor.id != project.manager_id:
            raise HTTPException(status_code=403, detail="Project manager permission required")
        ActivityRepository.add(db, ActivityLog(
            id=str(uuid4()), project_id=project.id, actor_id=actor.id,
            action="task.deleted", entity_type="task", entity_id=task.id,
            details=task.title,
        ))
        TaskRepository.delete(db, task)
        db.commit()
