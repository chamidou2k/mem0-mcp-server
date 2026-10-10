"""HTTP-priority, per-operation HTTPS fallback behavior.

Uses httpx.MockTransport to simulate the HTTP and HTTPS hub endpoints and
records which endpoint each operation reached.
"""

import asyncio

import certifi
import httpx
import pytest

import mem0_mcp_server as server


class Router:
    """Mutable mock hub handlers recording requests per endpoint."""

    def __init__(self):
        self.http_up = True
        self.https_up = True
        self.http_calls = []
        self.https_calls = []

    @staticmethod
    def _dispatch(up, calls, request, memory_id):
        calls.append((request.method, request.url.path))
        if not up:
            raise httpx.ConnectError("endpoint down", request=request)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/memories" and request.method == "POST":
            return httpx.Response(200, json={"results": [{"id": memory_id}]})
        return httpx.Response(200, json={})

    def http_handler(self, request):
        return self._dispatch(self.http_up, self.http_calls, request, "http-1")

    def https_handler(self, request):
        return self._dispatch(self.https_up, self.https_calls, request, "https-1")


def make_client(router, with_https=True):
    """Build a Mem0Client whose transports are mock handlers."""
    client = server.Mem0Client(host="http://hub:8001")
    client.client = httpx.AsyncClient(
        base_url="http://hub:8001",
        transport=httpx.MockTransport(router.http_handler),
    )
    if with_https:
        client.https_host = "https://hub:8443"
        client.https_client = httpx.AsyncClient(
            base_url="https://hub:8443",
            transport=httpx.MockTransport(router.https_handler),
        )
    return client


def run(coro):
    return asyncio.run(coro)


def test_http_healthy_uses_http_only():
    router = Router()
    client = make_client(router)

    result = run(client.add_memory("hello"))

    assert result == {"results": [{"id": "http-1"}]}
    assert ("GET", "/health") in router.http_calls
    assert ("POST", "/memories") in router.http_calls
    assert router.https_calls == []


def test_http_down_falls_back_to_https():
    router = Router()
    router.http_up = False
    client = make_client(router)

    result = run(client.add_memory("hello"))

    assert result == {"results": [{"id": "https-1"}]}
    assert ("POST", "/memories") in router.https_calls


def test_http_recovers_returns_to_http():
    router = Router()
    router.http_up = False
    client = make_client(router)

    run(client.add_memory("first"))
    assert ("POST", "/memories") in router.https_calls

    router.http_up = True
    run(client.add_memory("second"))

    # HTTP served exactly the recovered operation; HTTPS served only the first.
    assert router.http_calls.count(("POST", "/memories")) == 1
    assert router.https_calls.count(("POST", "/memories")) == 1


def test_http_down_without_https_endpoint_surfaces_error():
    router = Router()
    router.http_up = False
    client = make_client(router, with_https=False)

    with pytest.raises(httpx.HTTPError):
        run(client.add_memory("hello"))


def test_both_endpoints_down_surfaces_error():
    router = Router()
    router.http_up = False
    router.https_up = False
    client = make_client(router)

    with pytest.raises(httpx.HTTPError):
        run(client.add_memory("hello"))


def test_legacy_http_only_does_not_probe_status():
    # With no HTTPS endpoint configured, no availability probe is performed.
    router = Router()
    client = make_client(router, with_https=False)

    run(client.add_memory("hello"))

    assert ("GET", "/health") not in router.http_calls
    assert ("POST", "/memories") in router.http_calls


def test_https_only_uses_https_without_probe():
    # HTTPS configured alone: operations go straight to HTTPS, no HTTP probe.
    router = Router()
    client = server.Mem0Client(
        host=None, https_host="https://hub:8443", cert_path=certifi.where()
    )
    client.https_client = httpx.AsyncClient(
        base_url="https://hub:8443",
        transport=httpx.MockTransport(router.https_handler),
    )

    result = run(client.add_memory("hello"))

    assert result == {"results": [{"id": "https-1"}]}
    assert router.http_calls == []
    assert ("GET", "/health") not in router.https_calls
    assert ("POST", "/memories") in router.https_calls


def test_neither_endpoint_configured_raises_naming_options():
    client = server.Mem0Client(host=None)

    with pytest.raises(RuntimeError, match="mem0_host or mem0_host_https"):
        run(client.add_memory("hello"))
