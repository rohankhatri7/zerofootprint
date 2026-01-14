from fastapi import Depends, HTTPException, Header
from sqlmodel import Session
from db import get_session
from models.user import User
from security.jwt import decode_token
from settings import settings


def get_current_user(
    session: Session = Depends(get_session),
    authorization: str | None = Header(default=None),
    x_dev_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> User:
    if x_dev_api_key and x_user_id:
        if not settings.dev_api_key or x_dev_api_key != settings.dev_api_key:
            raise HTTPException(status_code=401, detail="Invalid dev key")
        user = session.get(User, int(x_user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
