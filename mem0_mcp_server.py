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
import sys
from typing import Optional

import httpx
from mcp.server.mcpserver import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mem0-mcp")

# Default configuration
DEFAULT_CONFIG = {
    "mem0_host": "http://192.168.1.100:8001",
    "api_key": "none",
    "user_id": "ssc",
    "agent_id": "opencode",
    "channel": "",
    "search_threshold": 0.1,
    "max_memories": 50,
    "infer": True,
}


class Mem0Client:
    """Client for interacting with remote mem0 REST API."""

    def __init__(
        self,
        host: str,
        api_key: str = "none",
        user_id: str = "ssc",
        agent_id: str = "opencode",
        channel: str = "",
        search_threshold: float = 0.1,
        max_memories: int = 50,
        infer: bool = False,
    ):
        self.host = host.rstrip("/")
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
        if channel:
            headers["X-Mem0-Source"] = channel
        headers["X-Mem0-Client"] = "mem0-mcp"
        self.client = httpx.AsyncClient(
            base_url=self.host,
            timeout=30.0,
            headers=headers,
        )

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

        response = await self.client.post("/memories", json=payload)
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

        response = await self.client.post("/search", json=payload)
        response.raise_for_status()
        return response.json()

    async def list_memories(self, page: int = 1, page_size: int = 50) -> dict:
        """List all memories for the user."""
        params = {"user_id": self.user_id}
        if self.agent_id:
            params["agent_id"] = self.agent_id
        params["top_k"] = min(page_size, self.max_memories)

        response = await self.client.get("/memories", params=params)
        response.raise_for_status()
        return response.json()

    async def get_memory(self, memory_id: str) -> dict:
        """Get a specific memory by ID."""
        response = await self.client.get(
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
        response = await self.client.delete(f"/memories/{memory_id}")
        response.raise_for_status()
        return response.json()

    async def update_memory(
        self, memory_id: str, content: str, metadata: Optional[dict] = None
    ) -> dict:
        """Update an existing memory."""
        payload = {"text": content}
        if metadata:
            payload["metadata"] = metadata
        response = await self.client.put(f"/memories/{memory_id}", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_status(self) -> dict:
        """Get mem0 server status."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from file or environment variables."""
    config = DEFAULT_CONFIG.copy()

    # Load from config file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config.update(json.load(f))

    # Override with environment variables
    env_mappings = {
        "MEM0_HOST": "mem0_host",
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

    return config


async def create_mcp_server(config: dict) -> MCPServer:
    """Create and configure the MCP server with all tool handlers."""
    mcp = MCPServer(name="mem0-mcp", version="1.0.0")

    mem0_client = Mem0Client(
        host=config["mem0_host"],
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
                {"status": "success", "message": "Mem0 server is healthy", "data": result},
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    return mcp


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Mem0 MCP Server")
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
    logger.info(f"Mem0 host: {config['mem0_host']}")
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
