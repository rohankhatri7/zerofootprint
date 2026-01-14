from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from google_auth_oauthlib.flow import Flow
import httpx
from uuid import uuid4
from db import get_session
from models.user import User
from security.jwt import create_token
from services.redis_client import get_redis
from settings import settings
from gmail.auth import PROFILE_SCOPES

router = APIRouter(prefix="/auth/google", tags=["auth"])


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


@router.get("/login")
def google_login(request: Request):
    redirect_uri = str(request.url_for("google_callback"))
    flow = build_flow(redirect_uri, PROFILE_SCOPES)
    state = str(uuid4())
    redis = get_redis()
    redis.setex(f"state:login:{state}", 600, "1")
    auth_url, _ = flow.authorization_url(
        access_type="online",
        include_granted_scopes="true",
        state=state,
        prompt="select_account",
    )
    return {"auth_url": auth_url}


@router.get("/callback", name="google_callback")
def google_callback(request: Request, session: Session = Depends(get_session)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    redis = get_redis()
    if not redis.get(f"state:login:{state}"):
        raise HTTPException(status_code=400, detail="Invalid state")

    redirect_uri = str(request.url_for("google_callback"))
    flow = build_flow(redirect_uri, PROFILE_SCOPES)
    flow.fetch_token(code=code)
    credentials = flow.credentials

    userinfo = {}
    if credentials and credentials.token:
        with httpx.Client() as client:
            resp = client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {credentials.token}"},
                timeout=10,
            )
            resp.raise_for_status()
            userinfo = resp.json()

    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("given_name") or "User"
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")

    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        user = User(email=email, name=name)
        session.add(user)
        session.commit()
        session.refresh(user)

    token = create_token(user.id, user.email)
    redirect = f"{settings.frontend_origin}/auth/callback?token={token}"
    return RedirectResponse(url=redirect)
