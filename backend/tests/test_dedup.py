from services.scan import upsert_service


def test_deduplication(session):
    service1 = upsert_service(session, 1, "mail.acme.com", "Acme")
    session.commit()
    service2 = upsert_service(session, 1, "login.acme.com", "Acme")
    session.commit()

    assert service1.id == service2.id
    assert service2.evidence_count == 2
    assert service2.domain == "acme.com"
