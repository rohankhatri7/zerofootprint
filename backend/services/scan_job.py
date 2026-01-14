from sqlmodel import Session
from db import engine
from services.gmail_service import get_gmail_client
from services.scan import build_scan_query, collect_services


def run_scan_for_user(user_id: int) -> int:
    with Session(engine) as session:
        client = get_gmail_client(session, user_id)
        query = build_scan_query()
        messages = client.list_candidate_messages(query)
        metadata_map = {}
        for msg in messages:
            msg_id = msg.get("id")
            if msg_id:
                metadata_map[msg_id] = client.get_message_metadata(msg_id)
        collect_services(session, user_id, messages, metadata_map)
        session.commit()
        return len(messages)
