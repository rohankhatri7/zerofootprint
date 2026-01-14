import pytest
from sqlmodel import SQLModel, Session, create_engine
from models.user import User
from models.service_account import ServiceAccount
from models.email_connection import EmailConnection
from models.privacy_request import PrivacyRequest
from models.request_log import RequestLog


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
