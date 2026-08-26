import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories.alert import AlertRepository
from app.schemas.alert import AlertPage, AlertStatus


class AlertNotFoundError(Exception):
    pass


class InvalidAlertStatusTransitionError(Exception):
    pass


class AlertService:
    ALLOWED_TRANSITIONS = {
        "open": {
            "investigating",
            "resolved",
            "false_positive",
        },
        "investigating": {
            "open",
            "resolved",
            "false_positive",
        },
        "resolved": {
            "investigating",
        },
        "false_positive": {
            "investigating",
        },
    }

    def __init__(
        self,
        repository: AlertRepository | None = None,
    ) -> None:
        self.repository = repository or AlertRepository()

    def get_alert(
        self,
        db: Session,
        alert_id: uuid.UUID,
    ) -> Alert:
        alert = self.repository.get_by_id(
            db,
            alert_id,
        )

        if alert is None:
            raise AlertNotFoundError

        return alert

    def list_alerts(
        self,
        db: Session,
        *,
        limit: int,
        offset: int,
        severity: str | None = None,
        status: str | None = None,
        source_ip: str | None = None,
    ) -> AlertPage:
        total, alerts = self.repository.list_alerts(
            db,
            limit=limit,
            offset=offset,
            severity=severity,
            status=status,
            source_ip=source_ip,
        )

        return AlertPage(
            total=total,
            limit=limit,
            offset=offset,
            returned=len(alerts),
            items=list(alerts),
        )

    def update_alert_status(
        self,
        db: Session,
        alert_id: uuid.UUID,
        new_status: AlertStatus,
    ) -> Alert:
        alert = self.repository.get_by_id(
            db,
            alert_id,
        )

        if alert is None:
            raise AlertNotFoundError

        if alert.status == new_status.value:
            return alert

        allowed_statuses = self.ALLOWED_TRANSITIONS.get(
            alert.status,
            set(),
        )

        if new_status.value not in allowed_statuses:
            raise InvalidAlertStatusTransitionError

        try:
            updated_alert = self.repository.update_status(
                db,
                alert,
                new_status.value,
            )

            db.commit()
            db.refresh(updated_alert)

            return updated_alert

        except SQLAlchemyError:
            db.rollback()
            raise
