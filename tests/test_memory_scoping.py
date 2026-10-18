"""Memory read/write agent_id scoping.

Reads (list/get/search) scope only by user_id; writes (add/update) carry the
configured agent_id. Uses httpx.MockTransport to inspect the outgoing request.
"""

import asyncio
import json

import httpx

import mem0_mcp_server as server


class Router:
    """Mutable mock hub that records every request it receives."""

    def __init__(self):
        self.requests = []

    def handler(self, request):
        self.requests.append(request)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/memories" and request.method == "POST":
            return httpx.Response(200, json={"results": [{"id": "m1"}]})
        if request.url.path == "/memories" and request.method == "GET":
            return httpx.Response(200, json={"results": [{"id": "m1", "memory": "x"}]})
        if request.url.path == "/memories/m1" and request.method == "PUT":
            return httpx.Response(200, json={"id": "m1"})
        if request.url.path == "/search" and request.method == "POST":
            return httpx.Response(200, json={"results": []})
        return httpx.Response(200, json={})


def make_client(router, agent_id="pi", user_id="test-user"):
    client = server.Mem0Client(
        host="http://hub:8001", user_id=user_id, agent_id=agent_id
    )
    client.client = httpx.AsyncClient(
        base_url="http://hub:8001",
        transport=httpx.MockTransport(router.handler),
    )
    return client


def run(coro):
    return asyncio.run(coro)


def last_request(router, method, path):
    matches = [
        r for r in router.requests if r.method == method and r.url.path == path
    ]
    assert matches, f"no {method} {path} request captured"
    return matches[-1]


def test_list_memories_scopes_by_user_only():
    router = Router()
    client = make_client(router)
    run(client.list_memories())
    req = last_request(router, "GET", "/memories")
    assert req.url.params["user_id"] == "test-user"
    assert "agent_id" not in req.url.params


def test_get_memory_scopes_by_user_only():
    router = Router()
    client = make_client(router)
    run(client.get_memory("m1"))
    req = last_request(router, "GET", "/memories")
    assert req.url.params["user_id"] == "test-user"
    assert "agent_id" not in req.url.params


def test_search_memories_omits_agent_id():
    router = Router()
    client = make_client(router)
    run(client.search_memories("hobby"))
    req = last_request(router, "POST", "/search")
    body = json.loads(req.content)
    assert body["user_id"] == "test-user"
    assert "agent_id" not in body


def test_add_memory_carries_agent_id():
    router = Router()
    client = make_client(router)
    run(client.add_memory("hello"))
    req = last_request(router, "POST", "/memories")
    body = json.loads(req.content)
    assert body["agent_id"] == "pi"


def test_update_memory_carries_agent_id():
    router = Router()
    client = make_client(router)
    run(client.update_memory("m1", "updated"))
    req = last_request(router, "PUT", "/memories/m1")
    body = json.loads(req.content)
    assert body["agent_id"] == "pi"
