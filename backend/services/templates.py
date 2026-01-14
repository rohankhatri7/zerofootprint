from typing import Tuple
from models.service_account import ServiceAccount


def draft_template(service: ServiceAccount, request_type: str, regime: str | None = None) -> Tuple[str, str]:
    subject = f"Privacy request for {service.service_name}"
    if request_type == "unsubscribe":
        body = (
            f"Hello {service.service_name} team,\n\n"
            "Please unsubscribe me from all marketing emails and mailing lists. "
            "Please confirm once complete.\n\n"
            "Thank you"
        )
        return subject, body

    if regime == "gdpr":
        body = (
            f"Hello {service.service_name} team,\n\n"
            "I am requesting deletion of my personal data and closure of my account. "
            "This request is made under GDPR. "
            "Please confirm once complete.\n\n"
            "Thank you"
        )
        return subject, body

    if regime == "ccpa":
        body = (
            f"Hello {service.service_name} team,\n\n"
            "I am requesting deletion of my personal data and closure of my account. "
            "This request is made under CCPA. "
            "Please confirm once complete.\n\n"
            "Thank you"
        )
        return subject, body

    body = (
        f"Hello {service.service_name} team,\n\n"
        "I am requesting deletion of my personal data and closure of my account. "
        "Please confirm once complete.\n\n"
        "Thank you"
    )
    return subject, body
