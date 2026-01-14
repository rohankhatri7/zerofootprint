from fastapi import Header, HTTPException
from settings import settings


def require_dev_api_key(x_dev_api_key: str | None = Header(default=None)) -> None:
    if not settings.dev_api_key:
        raise HTTPException(status_code=500, detail="DEV_API_KEY not set")
    if x_dev_api_key != settings.dev_api_key:
        raise HTTPException(status_code=401, detail="Invalid dev key")
