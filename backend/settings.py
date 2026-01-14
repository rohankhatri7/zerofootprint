import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://zerofootprint:zerofootprint@localhost:5432/zerofootprint",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")
    dev_api_key: str = os.getenv("DEV_API_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "")


settings = Settings()
