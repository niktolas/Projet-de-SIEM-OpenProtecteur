import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.security_event import (
    SecurityEventCreate,
    SecurityEventPage,
    SecurityEventRead,
    SeverityLevel,
)
from app.services.security_event import (
    SecurityEventNotFoundError,
    SecurityEventService,
)


router = APIRouter(
    prefix="/events",
    tags=["Security events"],
)

service = SecurityEventService()


@router.post(
    "",
    response_model=SecurityEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_security_event(
    event_data: SecurityEventCreate,
    db: Session = Depends(get_db),
):
    return service.create_event(
        db,
        event_data,
    )


@router.get(
    "",
    response_model=SecurityEventPage,
)
def list_security_events(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    hostname: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    severity: SeverityLevel | None = Query(default=None),
    source_ip: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service.list_events(
        db,
        limit=limit,
        offset=offset,
        hostname=hostname,
        event_type=event_type,
        severity=severity.value if severity is not None else None,
        source_ip=source_ip,
    )


@router.get(
    "/{event_id}",
    response_model=SecurityEventRead,
)
def get_security_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return service.get_event(
            db,
            event_id,
        )

    except SecurityEventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        ) from exc


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_security_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    try:
        service.delete_event(
            db,
            event_id,
        )

    except SecurityEventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
