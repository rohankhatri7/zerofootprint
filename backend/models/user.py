from typing import Optional
from sqlmodel import SQLModel, Field
from models.base import utcnow
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    created_at: datetime = Field(default_factory=utcnow)
