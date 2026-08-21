import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent
from app.repositories.security_event import SecurityEventRepository
from app.schemas.security_event import (
    SecurityEventCreate,
    SecurityEventPage,
)


class SecurityEventNotFoundError(Exception):
    pass


class SecurityEventService:
    def __init__(
        self,
        repository: SecurityEventRepository | None = None,
    ) -> None:
        self.repository = repository or SecurityEventRepository()

    def create_event(
        self,
        db: Session,
        event_data: SecurityEventCreate,
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

        try:
            created_event = self.repository.create(
                db,
                security_event,
            )
            db.commit()
            db.refresh(created_event)

            return created_event

        except SQLAlchemyError:
            db.rollback()
            raise

    def get_event(
        self,
        db: Session,
        event_id: uuid.UUID,
    ) -> SecurityEvent:
        security_event = self.repository.get_by_id(
            db,
            event_id,
        )

        if security_event is None:
            raise SecurityEventNotFoundError

        return security_event

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
    ) -> SecurityEventPage:
        total, events = self.repository.list_events(
            db,
            limit=limit,
            offset=offset,
            hostname=hostname,
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
        )

        return SecurityEventPage(
            total=total,
            limit=limit,
            offset=offset,
            returned=len(events),
            items=list(events),
        )

    def delete_event(
        self,
        db: Session,
        event_id: uuid.UUID,
    ) -> None:
        security_event = self.repository.get_by_id(
            db,
            event_id,
        )

        if security_event is None:
            raise SecurityEventNotFoundError

        try:
            self.repository.delete(
                db,
                security_event,
            )
            db.commit()

        except SQLAlchemyError:
            db.rollback()
            raise
