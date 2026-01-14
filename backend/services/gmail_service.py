from sqlmodel import Session, select
from models.email_connection import EmailConnection
from security.crypto import decrypt_text
from gmail.auth import credentials_from_refresh_token, GMAIL_SCOPES
from gmail.client import GmailClient


class GmailConnectionError(Exception):
    pass


def get_gmail_client(session: Session, user_id: int) -> GmailClient:
    statement = select(EmailConnection).where(
        EmailConnection.user_id == user_id, EmailConnection.provider == "google"
    )
    connection = session.exec(statement).first()
    if not connection:
        raise GmailConnectionError("Gmail not connected")
    refresh_token = decrypt_text(connection.refresh_token_encrypted)
    credentials = credentials_from_refresh_token(refresh_token, GMAIL_SCOPES)
    return GmailClient(credentials)
