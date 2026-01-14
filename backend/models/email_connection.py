from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.base import utcnow


class EmailConnection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    provider: str = Field(index=True)
    refresh_token_encrypted: str
    scope: str
    created_at: datetime = Field(default_factory=utcnow)
