from email.utils import parseaddr


def extract_domain(from_header: str) -> str:
    _, email_addr = parseaddr(from_header)
    if "@" not in email_addr:
        return ""
    return email_addr.split("@", 1)[1].strip().lower()


def normalize_domain(domain: str) -> str:
    parts = [p for p in domain.split(".") if p]
    if len(parts) <= 2:
        return domain
    return ".".join(parts[-2:])


def infer_service_name(from_header: str, domain: str) -> str:
    name, _ = parseaddr(from_header)
    cleaned = name.strip()
    if cleaned:
        return cleaned
    base = normalize_domain(domain)
    return base.split(".")[0].title()
