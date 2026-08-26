from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.orm import Project, ProjectMember


class ProjectRepository:
    @staticmethod
    def get_by_id(db: Session, project_id: str) -> Project | None:
        return db.get(Project, project_id)

    @staticmethod
    def list(db: Session, *, page: int, page_size: int, status: str | None = None, manager_id: str | None = None):
        stmt = select(Project)
        count_stmt = select(func.count()).select_from(Project)
        if status:
            stmt = stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)
        if manager_id:
            stmt = stmt.where(Project.manager_id == manager_id)
            count_stmt = count_stmt.where(Project.manager_id == manager_id)
        stmt = stmt.order_by(Project.created_at.desc(), Project.id).offset((page - 1) * page_size).limit(page_size)
        items = list(db.scalars(stmt).all())
        total = int(db.scalar(count_stmt) or 0)
        return items, total

    @staticmethod
    def add(db: Session, project: Project) -> Project:
        db.add(project)
        return project

    @staticmethod
    def delete(db: Session, project: Project) -> None:
        db.delete(project)

    @staticmethod
    def get_member(db: Session, project_id: str, user_id: str) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        return db.scalar(stmt)

    @staticmethod
    def add_member(db: Session, member: ProjectMember) -> ProjectMember:
        db.add(member)
        return member
