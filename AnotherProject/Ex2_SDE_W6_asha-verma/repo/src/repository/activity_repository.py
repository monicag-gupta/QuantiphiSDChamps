from sqlalchemy.orm import Session

from src.models.orm import ActivityLog


class ActivityRepository:
    @staticmethod
    def add(db: Session, log: ActivityLog) -> ActivityLog:
        db.add(log)
        return log
