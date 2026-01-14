import os
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEV_API_KEY = os.getenv("DEV_API_KEY", "")

mcp = FastMCP("zerofootprint")

def _client():
    return httpx.Client(
        base_url=BACKEND_URL,
        headers={"X-Dev-Api-Key": DEV_API_KEY},
        timeout=20,
    )

@mcp.tool()
def trigger_scan(user_id: int) -> dict:
    """Trigger a Gmail scan for a user."""
    with _client() as client:
        res = client.post("/gmail/scan", headers={"X-User-Id": str(user_id)})
        res.raise_for_status()
        return res.json()

@mcp.tool()
def list_services(user_id: int) -> list:
    """List discovered services for a user."""
    with _client() as client:
        res = client.get("/services", headers={"X-User-Id": str(user_id)})
        res.raise_for_status()
        return res.json()


@mcp.tool()
def create_request_draft(user_id: int, service_account_id: int, request_type: str) -> dict:
    """Create a request draft email."""
    with _client() as client:
        res = client.post(
            "/requests/draft",
            headers={"X-User-Id": str(user_id)},
            json={
                "service_account_id": service_account_id,
                "request_type": request_type,
            },
        )
        res.raise_for_status()
        return res.json()


@mcp.tool()
def send_request(
    user_id: int,
    service_account_id: int,
    request_type: str,
    to: str,
    subject: str,
    body: str,
    confirm: bool,
) -> dict:
    """Send a request email after explicit confirmation."""
    if not confirm:
        return {"error": "Confirmation required"}
    with _client() as client:
        res = client.post(
            "/requests/send",
            headers={"X-User-Id": str(user_id)},
            json={
                "service_account_id": service_account_id,
                "request_type": request_type,
                "to": to,
                "subject": subject,
                "body": body,
                "confirm": True,
            },
        )
        res.raise_for_status()
        return res.json()


@mcp.tool()
def sync_status(user_id: int) -> dict:
    """Sync request status by reading inbox threads."""
    with _client() as client:
        res = client.post("/requests/sync", headers={"X-User-Id": str(user_id)})
        res.raise_for_status()
        return res.json()

if __name__ == "__main__":
    mcp.run()
