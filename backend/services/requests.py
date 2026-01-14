from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from models.privacy_request import PrivacyRequest
from models.request_log import RequestLog
from models.service_account import ServiceAccount
from services.templates import draft_template


class RequestError(Exception):
    pass


def create_draft(
    session: Session,
    user_id: int,
    service_account_id: int,
    request_type: str,
    regime: Optional[str] = None,
) -> dict:
    if request_type not in {"unsubscribe", "delete_close"}:
        raise RequestError("Invalid request type")
    service = session.get(ServiceAccount, service_account_id)
    if not service or service.user_id != user_id:
        raise RequestError("Service not found")
    subject, body = draft_template(service, request_type, regime)
    to_address = f"support@{service.domain}"
    return {"to": to_address, "subject": subject, "body": body}


def create_request_record(
    session: Session,
    user_id: int,
    service_account_id: int,
    request_type: str,
    gmail_thread_id: Optional[str],
    gmail_message_id: Optional[str],
) -> PrivacyRequest:
    now = datetime.now(timezone.utc)
    request = PrivacyRequest(
        user_id=user_id,
        service_account_id=service_account_id,
        request_type=request_type,
        status="pending",
        gmail_thread_id=gmail_thread_id,
        gmail_message_id=gmail_message_id,
        created_at=now,
        updated_at=now,
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    return request


def log_request_event(session: Session, request_id: int, event_type: str, payload: str) -> None:
    log = RequestLog(
        privacy_request_id=request_id,
        event_type=event_type,
        payload_json=payload,
    )
    session.add(log)
    session.commit()


def list_requests(session: Session, user_id: int) -> list[PrivacyRequest]:
    statement = select(PrivacyRequest).where(PrivacyRequest.user_id == user_id)
    return list(session.exec(statement))
