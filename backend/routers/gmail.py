from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from sqlmodel import Session, select
from uuid import uuid4
from db import get_session
from models.email_connection import EmailConnection
from models.user import User
from security.crypto import encrypt_text
from security.deps import get_current_user
from services.redis_client import get_redis
from services.rate_limit import enforce_rate_limit, RateLimitError
from services.gmail_service import get_gmail_client
from services.scan import build_scan_query, collect_services
from gmail.auth import GMAIL_SCOPES
from settings import settings

router = APIRouter(prefix="/gmail", tags=["gmail"])


def build_flow(redirect_uri: str, scopes: list[str]) -> Flow:
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(client_config, scopes=scopes)
    flow.redirect_uri = redirect_uri
    return flow


@router.get("/connect/url")
def connect_url(request: Request, current_user: User = Depends(get_current_user)):
    state = str(uuid4())
    redis = get_redis()
    redis.setex(f"state:gmail:{state}", 600, str(current_user.id))
    redirect_uri = str(request.url_for("gmail_connect_callback"))
    flow = build_flow(redirect_uri, GMAIL_SCOPES)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent",
    )
    return {"auth_url": auth_url}


@router.get("/connect/callback", name="gmail_connect_callback")
def connect_callback(request: Request, session: Session = Depends(get_session)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    redis = get_redis()
    user_id = redis.get(f"state:gmail:{state}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid state")

    redirect_uri = str(request.url_for("gmail_connect_callback"))
    flow = build_flow(redirect_uri, GMAIL_SCOPES)
    flow.fetch_token(code=code)
    credentials = flow.credentials
    if not credentials or not credentials.refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    scopes = credentials.scopes or []
    if not set(GMAIL_SCOPES).issubset(set(scopes)):
        raise HTTPException(status_code=400, detail="Insufficient Gmail scopes")

    encrypted = encrypt_text(credentials.refresh_token)
    statement = select(EmailConnection).where(
        EmailConnection.user_id == int(user_id), EmailConnection.provider == "google"
    )
    connection = session.exec(statement).first()
    if connection:
        connection.refresh_token_encrypted = encrypted
        connection.scope = " ".join(scopes)
        session.add(connection)
    else:
        connection = EmailConnection(
            user_id=int(user_id),
            provider="google",
            refresh_token_encrypted=encrypted,
            scope=" ".join(scopes),
        )
        session.add(connection)
    session.commit()

    redirect = f"{settings.frontend_origin}/app?gmail=connected"
    return RedirectResponse(url=redirect)


@router.post("/scan")
def scan_inbox(
    async_scan: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    redis = get_redis()
    try:
        enforce_rate_limit(redis, f"scan:{current_user.id}")
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc))

    if async_scan:
        from services.jobs import get_queue
        from services.scan_job import run_scan_for_user

        queue = get_queue()
        job = queue.enqueue(run_scan_for_user, current_user.id)
        return {"queued": True, "job_id": job.id}

    client = get_gmail_client(session, current_user.id)
    query = build_scan_query()
    messages = client.list_candidate_messages(query)

    metadata_map = {}
    for msg in messages:
        msg_id = msg.get("id")
        if msg_id:
            metadata_map[msg_id] = client.get_message_metadata(msg_id)

    collect_services(session, current_user.id, messages, metadata_map)
    session.commit()
    return {"scanned": len(messages)}
