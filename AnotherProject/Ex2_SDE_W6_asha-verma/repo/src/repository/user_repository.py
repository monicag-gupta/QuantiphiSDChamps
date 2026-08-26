from sqlalchemy.orm import Session

from src.models.orm import User


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> User | None:
        return db.get(User, user_id)
