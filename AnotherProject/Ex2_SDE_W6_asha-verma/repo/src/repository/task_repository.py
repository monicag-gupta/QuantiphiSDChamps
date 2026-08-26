from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.orm import Risk, Task, TimeEntry


class TaskRepository:
    @staticmethod
    def get_by_id(db: Session, task_id: str) -> Task | None:
        return db.get(Task, task_id)

    @staticmethod
    def list_for_project(db: Session, project_id: str):
        stmt = select(Task).where(Task.project_id == project_id).order_by(Task.created_at, Task.id)
        items = list(db.scalars(stmt).all())
        return items, len(items)

    @staticmethod
    def add(db: Session, task: Task) -> Task:
        db.add(task)
        return task

    @staticmethod
    def delete(db: Session, task: Task) -> None:
        db.delete(task)

    @staticmethod
    def summary(db: Session, project_id: str) -> dict:
        today = date.today()
        tasks = list(db.scalars(select(Task).where(Task.project_id == project_id)).all())
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "done")
        blocked = sum(1 for t in tasks if t.status == "blocked")
        overdue = sum(1 for t in tasks if t.due_date and t.due_date < today and t.status not in {"done", "cancelled"})
        open_risks = int(db.scalar(select(func.count()).select_from(Risk).where(Risk.project_id == project_id, Risk.status == "open")) or 0)
        total_hours = float(db.scalar(
            select(func.coalesce(func.sum(TimeEntry.hours), 0.0))
            .join(Task, TimeEntry.task_id == Task.id)
            .where(Task.project_id == project_id)
        ) or 0.0)
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "blocked_tasks": blocked,
            "overdue_tasks": overdue,
            "completion_percentage": round((completed / total * 100) if total else 0.0, 2),
            "open_risks": open_risks,
            "total_logged_hours": round(total_hours, 2),
        }
