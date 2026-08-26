import uuid
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, ConfigDict


class AlertSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"

class AlertStatusUpdate(BaseModel):
    status: AlertStatus

class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rule_name: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source_ip: IPv4Address | IPv6Address | None
    username: str | None
    hostname: str | None
    event_count: int
    window_start: datetime
    window_end: datetime
    created_at: datetime


class AlertPage(BaseModel):
    total: int
    limit: int
    offset: int
    returned: int
    items: list[AlertRead]
