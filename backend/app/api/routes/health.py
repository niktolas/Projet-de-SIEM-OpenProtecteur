from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": "OpenProtecteur",
    }


@router.get("/database")
def database_health_check(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        database_name = db.execute(
            text("SELECT current_database()")
        ).scalar_one()

        return {
            "status": "healthy",
            "database": database_name,
        }

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable",
        ) from exc
