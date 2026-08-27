from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UsernameAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(
        self,
        repository: UserRepository | None = None,
    ) -> None:
        self.repository = repository or UserRepository()

    def create_user(
        self,
        db: Session,
        user_data: UserCreate,
    ) -> User:
        existing_user = self.repository.get_by_username(
            db,
            user_data.username,
        )

        if existing_user is not None:
            raise UsernameAlreadyExistsError

        user = User(
            username=user_data.username,
            password_hash=hash_password(
                user_data.password,
            ),
            role=user_data.role.value,
            is_active=True,
        )

        try:
            created_user = self.repository.create(
                db,
                user,
            )

            db.commit()
            db.refresh(created_user)

            return created_user

        except IntegrityError as exc:
            db.rollback()
            raise UsernameAlreadyExistsError from exc

        except SQLAlchemyError:
            db.rollback()
            raise

    def list_users(
        self,
        db: Session,
    ):
        return list(
            self.repository.list_users(db)
        )
