import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert import (
    AlertPage,
    AlertRead,
    AlertSeverity,
    AlertStatus,
    AlertStatusUpdate,
)
from app.services.alert import (
    AlertNotFoundError,
    AlertService,
    InvalidAlertStatusTransitionError,
)

from app.api.dependencies import require_roles
from app.models.user import User

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)

service = AlertService()


@router.get(
    "",
    response_model=AlertPage,
)
def list_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    severity: AlertSeverity | None = Query(default=None),
    alert_status: AlertStatus | None = Query(
        default=None,
        alias="status",
    ),
    current_user: User = Depends(
        require_roles("viewer", "analyst", "admin"),
    ),
    source_ip: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service.list_alerts(
        db,
        limit=limit,
        offset=offset,
        severity=severity.value if severity is not None else None,
        status=(
            alert_status.value
            if alert_status is not None
            else None
        ),
        source_ip=source_ip,
    )


@router.get(
    "/{alert_id}",
    response_model=AlertRead,
)
def get_alert(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("viewer", "analyst", "admin"),
    ),
):
    try:
        return service.get_alert(
            db,
            alert_id,
        )

    except AlertNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        ) from exc


@router.patch(
    "/{alert_id}/status",
    response_model=AlertRead,
)
def update_alert_status(
    alert_id: uuid.UUID,
    status_update: AlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("analyst", "admin"),
    ),
):
    try:
        return service.update_alert_status(
            db,
            alert_id,
            status_update.status,
        )

    except AlertNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        ) from exc

    except InvalidAlertStatusTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid alert status transition",
        ) from exc
