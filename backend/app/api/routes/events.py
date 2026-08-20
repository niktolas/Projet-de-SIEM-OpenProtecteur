from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.security_event import SecurityEvent
from app.schemas.security_event import (
    SecurityEventCreate,
    SecurityEventRead,
    SeverityLevel,
)


router = APIRouter(
    prefix="/events",
    tags=["Security events"],
)


@router.post(
    "",
    response_model=SecurityEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_security_event(
    event_data: SecurityEventCreate,
    db: Session = Depends(get_db),
) -> SecurityEvent:
    security_event = SecurityEvent(
        timestamp=event_data.timestamp or datetime.now(timezone.utc),
        source=event_data.source,
        hostname=event_data.hostname,
        event_type=event_data.event_type,
        username=event_data.username,
        source_ip=(
            str(event_data.source_ip)
            if event_data.source_ip is not None
            else None
        ),
        severity=event_data.severity.value,
        message=event_data.message,
    )

    db.add(security_event)
    db.commit()
    db.refresh(security_event)

    return security_event


@router.get(
    "",
    response_model=list[SecurityEventRead],
)
def list_security_events(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    hostname: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    severity: SeverityLevel | None = Query(default=None),
    source_ip: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    statement = select(SecurityEvent)

    if hostname is not None:
        statement = statement.where(
            SecurityEvent.hostname == hostname
        )

    if event_type is not None:
        statement = statement.where(
            SecurityEvent.event_type == event_type
        )

    if severity is not None:
        statement = statement.where(
            SecurityEvent.severity == severity.value
        )

    if source_ip is not None:
        statement = statement.where(
            SecurityEvent.source_ip == source_ip
        )

    statement = (
        statement
        .order_by(SecurityEvent.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


@router.get("/count")
def count_security_events(
    db: Session = Depends(get_db),
) -> dict[str, int]:
    statement = select(func.count()).select_from(SecurityEvent)
    total = db.scalar(statement)

    return {
        "total": total or 0,
    }
