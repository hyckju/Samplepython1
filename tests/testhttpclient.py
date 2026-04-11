import pytest

from secure_app.httpclient import OutboundUrlPolicy, validate_outbound_url


def test_validate_outbound_url_allowlist_host() -> None:
    policy = OutboundUrlPolicy(allowed_hosts=frozenset({"example.com"}))
    parsed = validate_outbound_url("https://example.com/path", policy)
    assert parsed.hostname == "example.com"


def test_validate_outbound_url_blocks_non_https() -> None:
    policy = OutboundUrlPolicy(allowed_hosts=frozenset({"example.com"}))
    with pytest.raises(ValueError):
        validate_outbound_url("http://example.com/", policy)


def test_validate_outbound_url_blocks_localhost() -> None:
    policy = OutboundUrlPolicy(allowed_hosts=frozenset({"example.com"}))
    with pytest.raises(ValueError):
        validate_outbound_url("https://localhost/", policy)


def test_validate_outbound_url_blocks_private_ip_literal() -> None:
    policy = OutboundUrlPolicy(allowed_hosts=frozenset({"example.com"}))
    with pytest.raises(ValueError):
        validate_outbound_url("https://127.0.0.1/", policy)


def test_validate_outbound_url_blocks_not_allowlisted_host() -> None:
    policy = OutboundUrlPolicy(allowed_hosts=frozenset({"example.com"}))
    with pytest.raises(ValueError):
        validate_outbound_url("https://evil.com/", policy)
