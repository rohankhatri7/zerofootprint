from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from models.user import User
from models.service_account import ServiceAccount
from routers.requests import router as requests_router
from security.deps import get_current_user
from db import get_session


class FakeGmailClient:
    def send_email(self, to, subject, body, thread_id=None):
        return {"id": "msg_123", "threadId": "thread_456"}


def setup_app(session):
    app = FastAPI()
    app.include_router(requests_router)

    def override_session():
        yield session

    def override_user():
        return session.get(User, 1)

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_session] = override_session
    return app


def test_request_send_flow(monkeypatch):
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(id=1, email="test@example.com", name="Test")
        service = ServiceAccount(user_id=1, service_name="Acme", domain="acme.com")
        session.add(user)
        session.add(service)
        session.commit()

        app = setup_app(session)
        monkeypatch.setattr(
            "routers.requests.get_gmail_client",
            lambda *args, **kwargs: FakeGmailClient(),
        )
        client = TestClient(app)

        payload = {
            "to": "support@acme.com",
            "subject": "Privacy request for Acme",
            "body": "Please delete my data",
            "service_account_id": service.id,
            "request_type": "delete_close",
            "confirm": True,
        }
        res = client.post("/requests/send", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "pending"
