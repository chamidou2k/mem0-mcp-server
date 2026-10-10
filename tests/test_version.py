"""The server exposes its running version through every surface."""

import asyncio
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

import pytest

import mem0_mcp_server as server

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _no_endpoint_env(monkeypatch):
    """Keep these tests independent of any ambient hub configuration."""
    for var in (
        "MEM0_HOST",
        "MEM0_HOST_HTTPS",
        "MEM0_CERT_PATH",
        "MEM0_TLS_VERIFY_HOSTNAME",
    ):
        monkeypatch.delenv(var, raising=False)


def _status_payload(result) -> dict:
    return json.loads(result.content[0].text)


def test_create_mcp_server_uses_module_version():
    mcp = asyncio.run(server.create_mcp_server(server.load_config(None)))
    assert mcp.version == server.__version__
    assert mcp.name == "mem0-mcp"


def test_status_tool_success_payload_reports_server_version(monkeypatch):
    async def fake_get_status(self):
        return {"status": "ok"}

    monkeypatch.setattr(server.Mem0Client, "get_status", fake_get_status)
    mcp = asyncio.run(server.create_mcp_server(server.load_config(None)))

    payload = _status_payload(asyncio.run(mcp.call_tool("mem0_get_status", {})))

    assert payload["status"] == "success"
    assert payload["server_version"] == server.__version__


def test_status_tool_error_payload_reports_server_version():
    # No endpoint configured, so the tool returns its error payload.
    mcp = asyncio.run(server.create_mcp_server(server.load_config(None)))

    payload = _status_payload(asyncio.run(mcp.call_tool("mem0_get_status", {})))

    assert payload["status"] == "error"
    assert payload["server_version"] == server.__version__


def test_cli_version_option_prints_version_without_hub():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "mem0_mcp_server.py"), "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert server.__version__ in (result.stdout + result.stderr)


def test_installed_package_version_matches_module():
    try:
        installed = importlib.metadata.version("mem0-mcp-server")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("mem0-mcp-server is not installed in this environment")

    assert installed == server.__version__
