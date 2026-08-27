from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user import (
    UsernameAlreadyExistsError,
    UserService,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

service = UserService()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin"),
    ),
):
    try:
        return service.create_user(
            db,
            user_data,
        )

    except UsernameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        ) from exc


@router.get(
    "",
    response_model=list[UserRead],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin"),
    ),
):
    return service.list_users(db)
