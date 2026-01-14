from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.base import utcnow


class ServiceAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    service_name: str
    domain: str = Field(index=True)
    first_seen_at: datetime = Field(default_factory=utcnow)
    last_seen_at: datetime = Field(default_factory=utcnow)
    evidence_count: int = 0
