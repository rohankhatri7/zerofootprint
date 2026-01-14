from datetime import datetime, timedelta, timezone
import jwt
from settings import settings


class AuthError(Exception):
    pass


def create_token(user_id: int, email: str) -> str:
    if not settings.jwt_secret:
        raise AuthError("JWT_SECRET is required")
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    if not settings.jwt_secret:
        raise AuthError("JWT_SECRET is required")
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
