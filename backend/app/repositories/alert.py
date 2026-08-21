import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert


class AlertRepository:
    def create(
        self,
        db: Session,
        alert: Alert,
    ) -> Alert:
        db.add(alert)
        db.flush()
        db.refresh(alert)

        return alert

    def get_by_id(
        self,
        db: Session,
        alert_id: uuid.UUID,
    ) -> Alert | None:
        return db.get(Alert, alert_id)

    def find_recent_open_alert(
        self,
        db: Session,
        *,
        rule_name: str,
        source_ip: str,
        username: str | None,
        created_after: datetime,
    ) -> Alert | None:
        statement = (
            select(Alert)
            .where(
                Alert.rule_name == rule_name,
                Alert.source_ip == source_ip,
                Alert.username == username,
                Alert.status.in_(["open", "investigating"]),
                Alert.created_at >= created_after,
            )
            .order_by(Alert.created_at.desc())
            .limit(1)
        )

        return db.scalar(statement)

    def list_alerts(
        self,
        db: Session,
        *,
        limit: int,
        offset: int,
        severity: str | None = None,
        status: str | None = None,
        source_ip: str | None = None,
    ) -> tuple[int, Sequence[Alert]]:
        filters = []

        if severity is not None:
            filters.append(Alert.severity == severity)

        if status is not None:
            filters.append(Alert.status == status)

        if source_ip is not None:
            filters.append(Alert.source_ip == source_ip)

        count_statement = (
            select(func.count())
            .select_from(Alert)
            .where(*filters)
        )

        total = db.scalar(count_statement) or 0

        alerts_statement = (
            select(Alert)
            .where(*filters)
            .order_by(
                Alert.created_at.desc(),
                Alert.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        alerts = db.scalars(alerts_statement).all()

        return total, alerts
