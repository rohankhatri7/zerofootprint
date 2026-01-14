from services.parsing import extract_domain, normalize_domain, infer_service_name


def test_extract_domain():
    domain = extract_domain("Acme <hello@sub.acme.com>")
    assert domain == "sub.acme.com"


def test_normalize_domain():
    assert normalize_domain("sub.acme.com") == "acme.com"
    assert normalize_domain("acme.com") == "acme.com"


def test_infer_service_name():
    assert infer_service_name("Acme Team <hello@acme.com>", "acme.com") == "Acme Team"
    assert infer_service_name("<hello@acme.com>", "acme.com") == "Acme"
