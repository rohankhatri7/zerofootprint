from datetime import datetime, timezone
from typing import Dict, List
from sqlmodel import Session, select
from models.service_account import ServiceAccount
from services.parsing import extract_domain, normalize_domain, infer_service_name


SUBJECT_QUERY = "subject:(welcome OR verify OR account OR subscription OR confirm)"


def build_scan_query() -> str:
    return f"{SUBJECT_QUERY} newer_than:1y"


def upsert_service(
    session: Session, user_id: int, domain: str, service_name: str
) -> ServiceAccount:
    normalized = normalize_domain(domain)
    statement = select(ServiceAccount).where(
        ServiceAccount.user_id == user_id, ServiceAccount.domain == normalized
    )
    existing = session.exec(statement).first()
    now = datetime.now(timezone.utc)
    if existing:
        existing.last_seen_at = now
        existing.evidence_count += 1
        session.add(existing)
        return existing
    service = ServiceAccount(
        user_id=user_id,
        service_name=service_name,
        domain=normalized,
        first_seen_at=now,
        last_seen_at=now,
        evidence_count=1,
    )
    session.add(service)
    return service


def process_message_headers(
    session: Session, user_id: int, headers: Dict[str, str]
) -> ServiceAccount | None:
    from_header = headers.get("From", "")
    domain = extract_domain(from_header)
    if not domain:
        return None
    service_name = infer_service_name(from_header, domain)
    return upsert_service(session, user_id, domain, service_name)


def parse_headers(payload: dict) -> Dict[str, str]:
    headers = payload.get("payload", {}).get("headers", [])
    return {h.get("name"): h.get("value") for h in headers if h.get("name")}


def collect_services(
    session: Session, user_id: int, messages: List[dict], metadata_map: Dict[str, dict]
) -> List[ServiceAccount]:
    seen = []
    for msg in messages:
        msg_id = msg.get("id")
        if not msg_id:
            continue
        metadata = metadata_map.get(msg_id, {})
        headers = parse_headers(metadata)
        service = process_message_headers(session, user_id, headers)
        if service:
            seen.append(service)
    return seen
