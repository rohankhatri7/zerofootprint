from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.base import utcnow


class RequestLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    privacy_request_id: int = Field(index=True)
    event_type: str
    payload_json: str
    created_at: datetime = Field(default_factory=utcnow)
