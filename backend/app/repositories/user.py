import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def create(
        self,
        db: Session,
        user: User,
    ) -> User:
        db.add(user)
        db.flush()
        db.refresh(user)

        return user

    def get_by_id(
        self,
        db: Session,
        user_id: uuid.UUID,
    ) -> User | None:
        return db.get(User, user_id)

    def get_by_username(
        self,
        db: Session,
        username: str,
    ) -> User | None:
        statement = select(User).where(
            User.username == username,
        )

        return db.scalar(statement)

    def list_users(
        self,
        db: Session,
    ) -> Sequence:
        statement = select(User).order_by(
            User.username.asc(),
        )

        return db.scalars(statement).all()
