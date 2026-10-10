#!/usr/bin/env python3
"""
Mem0 MCP Server - Local bridge to remote mem0 REST API

This MCP server exposes mem0 memory operations via the Model Context Protocol,
connecting to a remote mem0 platform instance via REST API.

Usage:
    python mem0_mcp_server.py
    python mem0_mcp_server.py --config config.json
    python mem0_mcp_server.py --transport sse --port 8050
"""

import asyncio
import json
import logging
import os
import ssl
import sys
from typing import Optional

import httpx
from mcp.server.mcpserver import MCPServer

# Version of this server. Single source of truth: exposed through the MCP server
# metadata, the mem0_get_status tool, and the --version CLI option, and read by
# pyproject.toml to set the installed package version.
__version__ = "1.1.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mem0-mcp")

# Default configuration
DEFAULT_CONFIG = {
    # No built-in endpoint: empty/None means "not configured". Set `mem0_host`
    # (HTTP) and/or `mem0_host_https` (HTTPS) to enable hub access.
    "mem0_host": "",
    # Optional HTTPS endpoint for the hub. When set, the server prefers the HTTP
    # endpoint and falls back to this one when HTTP is unavailable. Requires
    # cert_path (a CA certificate/bundle used to verify the hub's TLS cert).
    "mem0_host_https": None,
    "cert_path": None,
    # When true (default), the hub's TLS certificate is verified against
    # cert_path including a hostname/IP match. Set to false to keep chain
    # verification against cert_path but skip the hostname/IP match (useful for
    # self-signed hub certificates without a matching SAN). Configuration-file
    # only; never disables TLS verification entirely.
    "tls_verify_hostname": True,
    "api_key": "none",
    "user_id": "ssc",
    "agent_id": "opencode",
    "channel": "",
    "search_threshold": 0.1,
    "max_memories": 50,
    "infer": True,
}


def _normalize_base_url(value: str, default_scheme: str) -> str:
    """Return a hub base URL with a scheme, defaulting when none is given.

    A value that already contains a scheme is preserved; a scheme-less value
    such as ``host:port`` gets ``default_scheme`` prepended. Trailing slashes
    are stripped to match the existing ``mem0_host`` handling.
    """
    value = str(value).strip()
    if "://" not in value:
        value = f"{default_scheme}://{value}"
    return value.rstrip("/")


def _is_configured(value) -> bool:
    """Return True when an endpoint option holds a usable, non-blank value.

    ``None``, ``""`` and whitespace-only values all mean "not configured", so
    an operator can switch an endpoint off without removing the key.
    """
    return value is not None and str(value).strip() != ""


def _parse_bool_option(value, default: bool) -> bool:
    """Parse a boolean config option.

    Accepts a JSON boolean and the strings ``"true"``/``"false"`` (case-
    insensitive). Any other value (including ``None``/absent) yields ``default``.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text == "true":
            return True
        if text == "false":
            return False
    return default


class Mem0Client:
    """Client for interacting with remote mem0 REST API."""

    def __init__(
        self,
        host: Optional[str] = None,
        api_key: str = "none",
        user_id: str = "ssc",
        agent_id: str = "opencode",
        channel: str = "",
        search_threshold: float = 0.1,
        max_memories: int = 50,
        infer: bool = False,
        https_host: Optional[str] = None,
        cert_path: Optional[str] = None,
        tls_verify_hostname: bool = True,
    ):
        self.host = host.rstrip("/") if host else None
        self.https_host = https_host.rstrip("/") if https_host else None
        self.cert_path = cert_path
        self.tls_verify_hostname = tls_verify_hostname
        self.api_key = api_key
        self.user_id = user_id
        self.agent_id = agent_id
        self.channel = channel
        self.search_threshold = search_threshold
        self.max_memories = max_memories
        self.infer = infer
        # Build headers: include X-Mem0-Source and X-Mem0-Client like the SDK does
        headers: dict = {}
        if api_key != "none":
            headers["Content-Type"] = "application/json"
        # Send the configured API key the way the hub expects it. An unset
        # (empty) or literal "none" key sends no header, preserving compatibility
        # with hubs that do not require authentication.
        if api_key and api_key != "none":
            headers["X-API-Key"] = api_key
        if channel:
            headers["X-Mem0-Source"] = channel
        headers["X-Mem0-Client"] = "mem0-mcp"
        self.headers = headers

        # Preferred HTTP endpoint (no TLS kwargs); built only when configured.
        self.client: Optional[httpx.AsyncClient] = None
        if self.host:
            self.client = httpx.AsyncClient(
                base_url=self.host,
                timeout=30.0,
                headers=headers,
            )
        # Optional HTTPS endpoint, verified against the configured CA; built
        # only when configured. Either client may be None.
        self.https_client: Optional[httpx.AsyncClient] = None
        if self.https_host:
            verify = self.cert_path
            if not self.tls_verify_hostname:
                # Verify the certificate chain against the configured CA but
                # skip the hostname/IP match. TLS verification stays mandatory.
                verify = ssl.create_default_context(cafile=self.cert_path)
                verify.check_hostname = False
            self.https_client = httpx.AsyncClient(
                base_url=self.https_host,
                timeout=30.0,
                headers=headers,
                verify=verify,
            )

    async def _select_client(self) -> httpx.AsyncClient:
        """Return the client for the next hub operation.

        Selection matrix:
        - neither endpoint configured -> raise a clear error per operation
          (startup still succeeds);
        - HTTPS only -> the HTTPS client, with no HTTP probe;
        - HTTP only -> the HTTP client, with no probe;
        - both -> HTTP is preferred: probe HTTP per operation and use it when it
          responds, otherwise fall back to the HTTPS client.
        """
        if self.client is None and self.https_client is None:
            raise RuntimeError(
                "no mem0 endpoint configured; set mem0_host or mem0_host_https"
            )
        if self.https_client is None:
            return self.client
        if self.client is None:
            return self.https_client
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return self.client
        except Exception as e:
            logger.warning(
                "HTTP endpoint %s unavailable (%s); falling back to HTTPS endpoint %s",
                self.host,
                e,
                self.https_host,
            )
            return self.https_client

    async def add_memory(self, content: str, metadata: Optional[dict] = None) -> dict:
        """Add a memory to mem0.

        Uses the LLM for fact extraction via the messages field.
        The infer parameter in config controls whether the LLM
        extracts facts (True) or stores the message text directly (False).
        """
        payload = {
            "messages": [{"role": "user", "content": content}],
            "user_id": self.user_id,
            "infer": self.infer,
        }
        if metadata:
            payload["metadata"] = metadata
        if self.agent_id:
            payload["agent_id"] = self.agent_id

        client = await self._select_client()
        response = await client.post("/memories", json=payload)
        response.raise_for_status()
        return response.json()

    async def search_memories(self, query: str, limit: int = 5) -> dict:
        """Search memories using semantic similarity."""
        payload = {
            "query": query,
            "user_id": self.user_id,
        }
        if self.agent_id:
            payload["agent_id"] = self.agent_id

        client = await self._select_client()
        response = await client.post("/search", json=payload)
        response.raise_for_status()
        return response.json()

    async def list_memories(self, page: int = 1, page_size: int = 50) -> dict:
        """List all memories for the user."""
        params = {"user_id": self.user_id}
        if self.agent_id:
            params["agent_id"] = self.agent_id
        params["top_k"] = min(page_size, self.max_memories)

        client = await self._select_client()
        response = await client.get("/memories", params=params)
        response.raise_for_status()
        return response.json()

    async def get_memory(self, memory_id: str) -> dict:
        """Get a specific memory by ID."""
        client = await self._select_client()
        response = await client.get(
            "/memories",
            params={
                "user_id": self.user_id,
                "agent_id": self.agent_id,
                "top_k": self.max_memories,
            },
        )
        response.raise_for_status()
        data = response.json()
        for mem in data.get("results", []):
            if mem.get("id") == memory_id:
                return mem
        return {"error": f"Memory with ID '{memory_id}' not found"}

    async def delete_memory(self, memory_id: str) -> dict:
        """Delete a memory by ID."""
        client = await self._select_client()
        response = await client.delete(f"/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    async def update_memory(
        self, memory_id: str, content: str, metadata: Optional[dict] = None
    ) -> dict:
        """Update an existing memory."""
        payload = {"text": content}
        if metadata:
            payload["metadata"] = metadata
        client = await self._select_client()
        response = await client.put(f"/memories/{memory_id}", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_status(self) -> dict:
        """Get mem0 server status from the active endpoint."""
        client = await self._select_client()
        response = await client.get("/health")
        response.raise_for_status()
        return response.json()


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from file or environment variables.

    Endpoints are optional and treated as configured only when non-blank:
    ``None``, empty, and whitespace-only values all mean "not configured".
    ``mem0_host`` (HTTP) and ``mem0_host_https`` (HTTPS) are normalized here;
    when the HTTPS endpoint is configured, ``cert_path`` is required and
    validated so failures surface at startup. These endpoint options are
    configuration-file only and have no environment-variable mappings (unlike
    ``mem0_host``).
    """
    config = DEFAULT_CONFIG.copy()

    # Load from config file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config.update(json.load(f))

    # Override with environment variables
    env_mappings = {
        "MEM0_HOST": "mem0_host",
        "MEM0_HOST_HTTPS": "mem0_host_https",
        "MEM0_CERT_PATH": "cert_path",
        "MEM0_TLS_VERIFY_HOSTNAME": "tls_verify_hostname",
        "MEM0_API_KEY": "api_key",
        "MEM0_USER_ID": "user_id",
        "MEM0_AGENT_ID": "agent_id",
        "MEM0_SEARCH_THRESHOLD": "search_threshold",
        "MEM0_MAX_MEMORIES": "max_memories",
        "MEM0_INFER": "infer",
    }

    for env_var, config_key in env_mappings.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            if config_key == "infer":
                config[config_key] = env_value.lower() in ("true", "1", "yes")
            elif config_key in ("search_threshold", "max_memories"):
                config[config_key] = type(config[config_key])(env_value)
            else:
                config[config_key] = env_value

    # Hostname-verification toggle (configuration-file only; safe default true).
    config["tls_verify_hostname"] = _parse_bool_option(
        config.get("tls_verify_hostname"), True
    )

    # Resolve the HTTP endpoint (scheme-less values default to http://).
    # An empty/whitespace/None value means the endpoint is not configured.
    http_host = config.get("mem0_host")
    config["mem0_host"] = (
        _normalize_base_url(http_host, "http") if _is_configured(http_host) else None
    )

    # Resolve the optional HTTPS endpoint and validate its CA certificate.
    https_host = config.get("mem0_host_https")
    if _is_configured(https_host):
        config["mem0_host_https"] = _normalize_base_url(https_host, "https")
        cert_path = config.get("cert_path")
        if not _is_configured(cert_path):
            raise ValueError(
                "cert_path is required when mem0_host_https is configured "
                "(path to the CA certificate/bundle used to verify the hub's "
                "HTTPS certificate)"
            )
        if not os.path.isfile(cert_path) or not os.access(cert_path, os.R_OK):
            raise ValueError(
                f"cert_path '{cert_path}' does not exist or is not readable"
            )
        config["cert_path"] = cert_path
    else:
        config["mem0_host_https"] = None
        config["cert_path"] = None

    return config


async def create_mcp_server(config: dict) -> MCPServer:
    """Create and configure the MCP server with all tool handlers."""
    mcp = MCPServer(name="mem0-mcp", version=__version__)

    mem0_client = Mem0Client(
        host=config.get("mem0_host"),
        https_host=config.get("mem0_host_https"),
        cert_path=config.get("cert_path"),
        tls_verify_hostname=config.get("tls_verify_hostname", True),
        api_key=config["api_key"],
        user_id=config["user_id"],
        agent_id=config.get("agent_id"),
        channel=config.get("channel", ""),
        search_threshold=config.get("search_threshold", 0.1),
        max_memories=config.get("max_memories", 50),
        infer=config.get("infer", False),
    )

    @mcp.tool()
    async def mem0_add_memory(content: str, metadata: Optional[dict] = None) -> str:
        """Add a new memory to mem0.

        Args:
            content: The memory content to store
            metadata: Optional metadata dictionary
        """
        try:
            result = await mem0_client.add_memory(content, metadata)
            return json.dumps(
                {"status": "success", "message": "Memory added", "data": result},
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    async def mem0_search_memories(query: str, limit: int = 5) -> str:
        """Search memories using semantic similarity.

        Args:
            query: The search query
            limit: Maximum number of results (default: 5)
        """
        try:
            result = await mem0_client.search_memories(query, limit)
            return json.dumps(
                {
                    "status": "success",
                    "message": f"Found {len(result.get('results', []))} memories",
                    "data": result,
                },
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    async def mem0_list_memories(page: int = 1, page_size: int = 20) -> str:
        """List all memories for the current user.

        Args:
            page: Page number for pagination (default: 1)
            page_size: Memories per page (default: 20, max: 50)
        """
        try:
            result = await mem0_client.list_memories(page, page_size)
            return json.dumps(
                {
                    "status": "success",
                    "message": f"Retrieved {len(result.get('results', []))} memories",
                    "data": result,
                },
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error listing memories: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    async def mem0_get_memory(memory_id: str) -> str:
        """Get a specific memory by ID.

        Args:
            memory_id: The ID of the memory to retrieve
        """
        try:
            result = await mem0_client.get_memory(memory_id)
            return json.dumps(
                {
                    "status": "success",
                    "message": "Memory retrieved",
                    "data": result,
                },
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error getting memory: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    async def mem0_delete_memory(memory_id: str) -> str:
        """Delete a memory by ID.

        Args:
            memory_id: The ID of the memory to delete
        """
        try:
            result = await mem0_client.delete_memory(memory_id)
            return json.dumps(
                {"status": "success", "message": "Memory deleted", "data": result},
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    async def mem0_update_memory(
        memory_id: str, content: str, metadata: Optional[dict] = None
    ) -> str:
        """Update an existing memory.

        Args:
            memory_id: The ID of the memory to update
            content: The new content for the memory
            metadata: Optional new metadata
        """
        try:
            result = await mem0_client.update_memory(memory_id, content, metadata)
            return json.dumps(
                {"status": "success", "message": "Memory updated", "data": result},
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    async def mem0_get_status() -> str:
        """Get the status of the mem0 server connection."""
        try:
            result = await mem0_client.get_status()
            return json.dumps(
                {
                    "status": "success",
                    "message": "Mem0 server is healthy",
                    "server_version": __version__,
                    "data": result,
                },
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return json.dumps(
                {"status": "error", "message": str(e), "server_version": __version__}
            )

    return mcp


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Mem0 MCP Server")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("--config", type=str, help="Path to configuration file (JSON)", default=None)
    parser.add_argument("--host", type=str, help="Host to bind to (default: 0.0.0.0)", default=None)
    parser.add_argument("--port", type=int, help="Port to listen on (default: 8050)", default=None)
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        help="Transport mode (default: stdio)",
        default="stdio",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    logger.info(f"Mem0 MCP Server starting...")
    if config.get("mem0_host"):
        logger.info(f"Mem0 HTTP host: {config['mem0_host']}")
    else:
        logger.info("Mem0 HTTP host: not configured")
    if config.get("mem0_host_https"):
        logger.info(
            f"Mem0 HTTPS host (fallback): {config['mem0_host_https']} "
            f"(CA: {config.get('cert_path')})"
        )
    if not config.get("mem0_host") and not config.get("mem0_host_https"):
        logger.warning(
            "No mem0 endpoint configured; hub operations will fail until "
            "mem0_host or mem0_host_https is set"
        )
    logger.info(f"User ID: {config['user_id']}")
    logger.info(f"Agent ID: {config.get('agent_id', 'N/A')}")

    mcp = asyncio.run(create_mcp_server(config))

    transport = args.transport
    host = args.host or "0.0.0.0"
    port = args.port or 8050

    logger.info(f"Starting {transport} server on {host}:{port}")

    if transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
