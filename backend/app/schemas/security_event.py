import uuid
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, ConfigDict, Field

#Le modele SQLAlchemy represente les donnees dans PostgreSQL. Les schemas Pydantic representent les donnees acceptees et retournees par l’API.

class SeverityLevel(str, Enum):
    informational = "informational"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class SecurityEventCreate(BaseModel):
    timestamp: datetime | None = None

    source: str = Field(
        min_length=1,
        max_length=100,
        examples=["linux_auth"],
    )

    hostname: str = Field(
        min_length=1,
        max_length=255,
        examples=["srv-linux-01"],
    )

    event_type: str = Field(
        min_length=1,
        max_length=100,
        examples=["authentication_failure"],
    )

    username: str | None = Field(
        default=None,
        max_length=255,
        examples=["admin"],
    )

    source_ip: IPv4Address | IPv6Address | None = Field(
        default=None,
        examples=["192.168.5.67"],
    )

    severity: SeverityLevel = SeverityLevel.informational

    message: str | None = Field(
        default=None,
        max_length=5000,
        examples=["Failed SSH authentication"],
    )


class SecurityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: datetime
    source: str
    hostname: str
    event_type: str
    username: str | None
    source_ip: IPv4Address | IPv6Address | None
    severity: SeverityLevel
    message: str | None
    created_at: datetime
