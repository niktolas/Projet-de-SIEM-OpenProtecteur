import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent


class SecurityEventRepository:
    def create(
        self,
        db: Session,
        security_event: SecurityEvent,
    ) -> SecurityEvent:
        db.add(security_event)
        db.flush()
        db.refresh(security_event)

        return security_event

    def get_by_id(
        self,
        db: Session,
        event_id: uuid.UUID,
    ) -> SecurityEvent | None:
        return db.get(SecurityEvent, event_id)

    def list_events(
        self,
        db: Session,
        *,
        limit: int,
        offset: int,
        hostname: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        source_ip: str | None = None,
    ) -> tuple[int, Sequence[SecurityEvent]]:
        filters = []

        if hostname is not None:
            filters.append(SecurityEvent.hostname == hostname)

        if event_type is not None:
            filters.append(SecurityEvent.event_type == event_type)

        if severity is not None:
            filters.append(SecurityEvent.severity == severity)

        if source_ip is not None:
            filters.append(SecurityEvent.source_ip == source_ip)

        count_statement = (
            select(func.count())
            .select_from(SecurityEvent)
            .where(*filters)
        )

        total = db.scalar(count_statement) or 0

        events_statement = (
            select(SecurityEvent)
            .where(*filters)
            .order_by(
                SecurityEvent.timestamp.desc(),
                SecurityEvent.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        events = db.scalars(events_statement).all()

        return total, events

    def delete(
        self,
        db: Session,
        security_event: SecurityEvent,
    ) -> None:
        db.delete(security_event)
        db.flush()
