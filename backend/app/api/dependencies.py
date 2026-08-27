import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import (
    InvalidAccessTokenError,
    decode_access_token,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
)


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])

    except (
        InvalidAccessTokenError,
        ValueError,
        KeyError,
    ) as exc:
        raise authentication_error() from exc

    user = UserRepository().get_by_id(
        db,
        user_id,
    )

    if user is None or not user.is_active:
        raise authentication_error()

    return user


def require_roles(
    *allowed_roles: str,
) -> Callable:
    def role_dependency(
        current_user: User = Depends(
            get_current_user,
        ),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_dependency
