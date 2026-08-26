from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.repository.user_repository import UserRepository
from src.models.orm import User

DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DBSession,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> User:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header is required")
    user = UserRepository.get_by_id(db, x_user_id)
    if not user or not user.active:
        raise HTTPException(status_code=404, detail="Active user not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
