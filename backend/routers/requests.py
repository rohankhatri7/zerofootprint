from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.user import User
from models.privacy_request import PrivacyRequest
from security.deps import get_current_user
from services.requests import create_draft, create_request_record, list_requests, RequestError, log_request_event
from services.gmail_service import get_gmail_client
from services.status_sync import evaluate_status, update_request_status

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("/draft")
def draft_request(
    payload: dict,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_draft(
            session,
            current_user.id,
            payload.get("service_account_id"),
            payload.get("request_type"),
            payload.get("regime"),
        )
    except RequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/send")
def send_request(
    payload: dict,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not payload.get("confirm"):
        raise HTTPException(status_code=400, detail="Confirmation required")

    to_addr = payload.get("to")
    subject = payload.get("subject")
    body = payload.get("body")
    service_account_id = payload.get("service_account_id")
    request_type = payload.get("request_type")
    if not all([to_addr, subject, body, service_account_id, request_type]):
        raise HTTPException(status_code=400, detail="Missing fields")
    if request_type not in {"unsubscribe", "delete_close"}:
        raise HTTPException(status_code=400, detail="Invalid request type")

    client = get_gmail_client(session, current_user.id)
    response = client.send_email(to_addr, subject, body)
    request = create_request_record(
        session,
        current_user.id,
        service_account_id,
        request_type,
        response.get("threadId"),
        response.get("id"),
    )
    log_request_event(session, request.id, "sent", "{}")
    return {"id": request.id, "status": request.status}


@router.post("/sync")
def sync_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    client = get_gmail_client(session, current_user.id)
    statement = select(PrivacyRequest).where(
        PrivacyRequest.user_id == current_user.id,
        PrivacyRequest.status.in_(["pending", "needs_info"]),
        PrivacyRequest.gmail_thread_id.is_not(None),
    )
    pending = list(session.exec(statement))
    updated = 0
    for req in pending:
        messages = client.list_thread_messages(req.gmail_thread_id)
        status = evaluate_status(messages)
        if status:
            update_request_status(session, req, status)
            updated += 1
    return {"checked": len(pending), "updated": updated}


@router.get("")
def get_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return list_requests(session, current_user.id)
