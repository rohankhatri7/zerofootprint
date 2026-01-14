from typing import List, Optional, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GmailClient:
    def __init__(self, credentials: Credentials):
        self._service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def list_candidate_messages(self, query: str, max_results: int = 200) -> List[Dict[str, Any]]:
        result = (
            self._service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        return result.get("messages", [])

    def get_message_metadata(self, message_id: str) -> Dict[str, Any]:
        return (
            self._service.users()
            .messages()
            .get(userId="me", id=message_id, format="metadata")
            .execute()
        )

    def send_email(
        self, to: str, subject: str, body: str, thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        payload: Dict[str, Any] = {"raw": raw}
        if thread_id:
            payload["threadId"] = thread_id
        return (
            self._service.users().messages().send(userId="me", body=payload).execute()
        )

    def list_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        thread = (
            self._service.users()
            .threads()
            .get(userId="me", id=thread_id, format="metadata")
            .execute()
        )
        return thread.get("messages", [])
