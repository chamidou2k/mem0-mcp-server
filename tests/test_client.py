"""Mem0Client wiring: which endpoints/clients are constructed and the headers sent."""

import ssl

import certifi
import pytest

import mem0_mcp_server as server


def test_http_only_client_has_no_https_client():
    client = server.Mem0Client(host="http://hub:8001")
    assert str(client.client.base_url).startswith("http://")
    assert client.https_client is None


def test_https_only_client_has_no_http_client():
    client = server.Mem0Client(
        host=None, https_host="https://hub:8443", cert_path=certifi.where()
    )
    assert client.client is None
    assert str(client.https_client.base_url).startswith("https://")


def test_both_endpoints_build_both_clients():
    client = server.Mem0Client(
        host="http://hub:8001", https_host="https://hub:8443", cert_path=certifi.where()
    )
    assert client.client is not None
    assert client.https_client is not None


def test_neither_endpoint_builds_no_clients():
    client = server.Mem0Client(host=None)
    assert client.client is None
    assert client.https_client is None


def test_https_client_built_with_configured_ca():
    ca = certifi.where()
    client = server.Mem0Client(
        host="http://hub:8001", https_host="https://hub:8443", cert_path=ca
    )

    assert str(client.client.base_url).startswith("http://")
    assert client.https_client is not None
    assert str(client.https_client.base_url).startswith("https://")

    # The HTTPS transport loaded a CA bundle and enforces verification.
    ctx = client.https_client._transport._pool._ssl_context
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.get_ca_certs()


def test_https_client_invalid_ca_path_is_rejected(tmp_path):
    bad = tmp_path / "bad.pem"
    bad.write_text("this is not a certificate")
    with pytest.raises((ssl.SSLError, OSError)):
        server.Mem0Client(host="http://hub:8001", https_host="https://hub:8443", cert_path=str(bad))


def test_https_client_default_verifies_hostname():
    ca = certifi.where()
    client = server.Mem0Client(
        host="http://hub:8001", https_host="https://hub:8443", cert_path=ca
    )
    ctx = client.https_client._transport._pool._ssl_context
    assert ctx.check_hostname is True
    assert ctx.verify_mode == ssl.CERT_REQUIRED


def test_https_client_can_skip_hostname_check():
    ca = certifi.where()
    client = server.Mem0Client(
        host="http://hub:8001",
        https_host="https://hub:8443",
        cert_path=ca,
        tls_verify_hostname=False,
    )
    ctx = client.https_client._transport._pool._ssl_context
    assert ctx.check_hostname is False
    assert ctx.verify_mode == ssl.CERT_REQUIRED


def test_api_key_header_sent_on_both_clients():
    client = server.Mem0Client(
        host="http://hub:8001",
        https_host="https://hub:8443",
        cert_path=certifi.where(),
        api_key="secret-key",
    )
    assert client.client.headers["X-API-Key"] == "secret-key"
    assert client.https_client.headers["X-API-Key"] == "secret-key"


def test_no_api_key_header_when_key_unset():
    client = server.Mem0Client(host="http://hub:8001")
    assert "X-API-Key" not in client.client.headers


def test_no_api_key_header_for_none_literal():
    client = server.Mem0Client(host="http://hub:8001", api_key="none")
    assert "X-API-Key" not in client.client.headers


def test_no_api_key_header_for_empty_key():
    client = server.Mem0Client(host="http://hub:8001", api_key="")
    assert "X-API-Key" not in client.client.headers
