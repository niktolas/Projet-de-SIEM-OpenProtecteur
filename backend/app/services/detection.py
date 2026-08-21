from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.security_event import SecurityEvent
from app.repositories.alert import AlertRepository
from app.repositories.security_event import SecurityEventRepository


class DetectionService:
    BRUTE_FORCE_RULE_NAME = "authentication_brute_force"
    BRUTE_FORCE_THRESHOLD = 5
    BRUTE_FORCE_WINDOW = timedelta(minutes=5)

    def __init__(
        self,
        event_repository: SecurityEventRepository | None = None,
        alert_repository: AlertRepository | None = None,
    ) -> None:
        self.event_repository = (
            event_repository or SecurityEventRepository()
        )
        self.alert_repository = (
            alert_repository or AlertRepository()
        )

    def analyze_event(
        self,
        db: Session,
        security_event: SecurityEvent,
    ) -> Alert | None:
        if security_event.event_type != "authentication_failure":
            return None

        if security_event.source_ip is None:
            return None

        source_ip = str(security_event.source_ip)
        window_end = security_event.timestamp
        window_start = window_end - self.BRUTE_FORCE_WINDOW

        failure_count = (
            self.event_repository.count_authentication_failures(
                db,
                source_ip=source_ip,
                username=security_event.username,
                window_start=window_start,
                window_end=window_end,
            )
        )

        if failure_count < self.BRUTE_FORCE_THRESHOLD:
            return None

        existing_alert = (
            self.alert_repository.find_recent_open_alert(
                db,
                rule_name=self.BRUTE_FORCE_RULE_NAME,
                source_ip=source_ip,
                username=security_event.username,
                created_after=window_start,
            )
        )

        if existing_alert is not None:
            return None

        username = security_event.username or "unknown"

        alert = Alert(
            rule_name=self.BRUTE_FORCE_RULE_NAME,
            title="Possible authentication brute force",
            description=(
                f"{failure_count} authentication failures "
                f"were detected for user {username} "
                f"from source IP {source_ip} "
                "within five minutes."
            ),
            severity="high",
            status="open",
            source_ip=source_ip,
            username=security_event.username,
            hostname=security_event.hostname,
            event_count=failure_count,
            window_start=window_start,
            window_end=window_end,
        )

        return self.alert_repository.create(
            db,
            alert,
        )
