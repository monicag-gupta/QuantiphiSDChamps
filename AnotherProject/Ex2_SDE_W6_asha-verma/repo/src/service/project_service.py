from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.schemas import MemberCreate, ProjectCreate, ProjectPatch
from src.models.orm import ActivityLog, Project, ProjectMember, User
from src.repository.activity_repository import ActivityRepository
from src.repository.project_repository import ProjectRepository
from src.repository.task_repository import TaskRepository
from src.repository.user_repository import UserRepository


class ProjectService:
    @staticmethod
    def _require_project(db: Session, project_id: str) -> Project:
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @staticmethod
    def _require_manager(project: Project, actor: User) -> None:
        if project.manager_id != actor.id:
            raise HTTPException(status_code=403, detail="Project manager permission required")

    @staticmethod
    def list_projects(db: Session, *, page: int, page_size: int, status: str | None, manager_id: str | None):
        items, total = ProjectRepository.list(db, page=page, page_size=page_size, status=status, manager_id=manager_id)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def create_project(db: Session, payload: ProjectCreate, actor: User) -> Project:
        project = Project(
            id=str(uuid4()),
            name=payload.name,
            description=payload.description,
            manager_id=actor.id,
            status=payload.status.value,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        ProjectRepository.add(db, project)
        db.flush()
        ProjectRepository.add_member(db, ProjectMember(
            id=str(uuid4()), project_id=project.id, user_id=actor.id, role="manager"
        ))
        ActivityRepository.add(db, ActivityLog(
            id=str(uuid4()), project_id=project.id, actor_id=actor.id,
            action="project.created", entity_type="project", entity_id=project.id,
            details=f"Created project {project.name}",
        ))
        db.commit()
        db.refresh(project)
        return project

    @classmethod
    def get_project(cls, db: Session, project_id: str) -> Project:
        return cls._require_project(db, project_id)

    @classmethod
    def patch_project(cls, db: Session, project_id: str, payload: ProjectPatch, actor: User) -> Project:
        project = cls._require_project(db, project_id)
        cls._require_manager(project, actor)
        changes = payload.model_dump(exclude_unset=True)
        proposed_start = changes.get("start_date", project.start_date)
        proposed_end = changes.get("end_date", project.end_date)
        if proposed_end < proposed_start:
            raise HTTPException(status_code=422, detail="end_date cannot be before start_date")
        for key, value in changes.items():
            if key == "status":
                value = value.value
            setattr(project, key, value)
        ActivityRepository.add(db, ActivityLog(
            id=str(uuid4()), project_id=project.id, actor_id=actor.id,
            action="project.updated", entity_type="project", entity_id=project.id,
            details=",".join(sorted(changes.keys())),
        ))
        db.commit()
        db.refresh(project)
        return project

    @classmethod
    def delete_project(cls, db: Session, project_id: str, actor: User) -> None:
        project = cls._require_project(db, project_id)
        cls._require_manager(project, actor)
        ProjectRepository.delete(db, project)
        db.commit()

    @classmethod
    def add_member(cls, db: Session, project_id: str, payload: MemberCreate, actor: User) -> ProjectMember:
        project = cls._require_project(db, project_id)
        cls._require_manager(project, actor)
        user = UserRepository.get_by_id(db, payload.user_id)
        if not user or not user.active:
            raise HTTPException(status_code=404, detail="Active user not found")
        if ProjectRepository.get_member(db, project_id, payload.user_id):
            raise HTTPException(status_code=409, detail="User is already a project member")
        member = ProjectMember(
            id=str(uuid4()), project_id=project_id, user_id=payload.user_id, role=payload.role.value
        )
        ProjectRepository.add_member(db, member)
        ActivityRepository.add(db, ActivityLog(
            id=str(uuid4()), project_id=project_id, actor_id=actor.id,
            action="member.added", entity_type="project_member", entity_id=member.id,
            details=f"user_id={payload.user_id};role={payload.role.value}",
        ))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="User is already a project member")
        db.refresh(member)
        return member

    @classmethod
    def summary(cls, db: Session, project_id: str) -> dict:
        cls._require_project(db, project_id)
        result = TaskRepository.summary(db, project_id)
        return {"project_id": project_id, **result}
