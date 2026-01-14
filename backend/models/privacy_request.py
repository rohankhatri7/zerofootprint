from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.base import utcnow


class PrivacyRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    service_account_id: int = Field(index=True)
    request_type: str
    status: str
    gmail_thread_id: Optional[str] = None
    gmail_message_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
