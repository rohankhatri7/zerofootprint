from datetime import datetime, timezone
from typing import List
from sqlmodel import Session
from models.privacy_request import PrivacyRequest
from models.request_log import RequestLog

COMPLETED_KEYWORDS = ["deleted", "removed", "closed your account"]
NEEDS_INFO_KEYWORDS = ["verify", "additional information"]


def _message_text(payload: dict) -> str:
    headers = payload.get("payload", {}).get("headers", [])
    subject = ""
    for header in headers:
        if header.get("name") == "Subject":
            subject = header.get("value", "")
    return subject.lower()


def evaluate_status(messages: List[dict]) -> str | None:
    combined = " ".join(_message_text(m) for m in messages)
    if any(k in combined for k in COMPLETED_KEYWORDS):
        return "completed"
    if any(k in combined for k in NEEDS_INFO_KEYWORDS):
        return "needs_info"
    return None


def update_request_status(session: Session, request: PrivacyRequest, new_status: str) -> None:
    request.status = new_status
    request.updated_at = datetime.now(timezone.utc)
    session.add(request)
    session.commit()

    log = RequestLog(
        privacy_request_id=request.id,
        event_type="sync",
        payload_json=f"status:{new_status}",
    )
    session.add(log)
    session.commit()
