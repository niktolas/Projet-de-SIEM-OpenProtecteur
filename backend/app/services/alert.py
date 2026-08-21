import uuid

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories.alert import AlertRepository
from app.schemas.alert import AlertPage


class AlertNotFoundError(Exception):
    pass


class AlertService:
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
