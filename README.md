# Mem0 MCP Server

A local MCP (Model Context Protocol) server that bridges to a remote mem0 REST API. Enables AI agents to access persistent memory through the mem0 platform.

## Features

- **Add memories** — Store new memories with semantic extraction
- **Search memories** — Find memories using semantic similarity
- **List memories** — Browse all stored memories with pagination
- **Get memory** — Retrieve a specific memory by ID
- **Update memory** — Modify existing memories
- **Delete memory** — Remove memories
- **Status check** — Verify mem0 server connectivity

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Or use the provided start script which creates a virtual environment automatically:

```bash
chmod +x start.sh
./start.sh
```

### 2. Configure

Copy `config.template.json` to `config.json` and update the values:

```bash
cp config.template.json config.json
```

Edit `config.json` with your mem0 server details:

```json
{
  "mem0_host": "http://<mem0-host>:<port>",
  "api_key": "<api_key>",
  "user_id": "<user_id>",
  "agent_id": "<agent_id>",
  "channel": "<channel>",
  "search_threshold": 0.1,
  "max_memories": 50,
  "infer": true
}
```

Or use environment variables (`MEM0_HOST`, `MEM0_USER_ID`, `MEM0_AGENT_ID`, `MEM0_API_KEY`, `MEM0_CHANNEL`, `MEM0_SEARCH_THRESHOLD`, `MEM0_MAX_MEMORIES`, `MEM0_INFER`).

### 3. Run

```bash
# Using start script (creates .venv automatically)
./start.sh

# Or directly
python mem0_mcp_server.py --config config.json

# SSE mode (network-accessible)
python mem0_mcp_server.py --config config.json --transport sse --port 8050
```

## Docker

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f mem0-mcp

# Stop
docker-compose down
```

## Configuration Reference

| Config Key | Env Variable | Default | Description |
|---|---|---|---|
| `mem0_host` | `MEM0_HOST` | `http://<mem0-host>:<port>` | Mem0 platform URL |
| `api_key` | `MEM0_API_KEY` | `none` | API key (use "none" if not required) |
| `user_id` | `MEM0_USER_ID` | `user` | Mem0 user identifier |
| `agent_id` | `MEM0_AGENT_ID` | `agent` | Mem0 agent identifier |
| `channel` | `MEM0_CHANNEL` | `` | Channel/source identifier |
| `search_threshold` | `MEM0_SEARCH_THRESHOLD` | `0.1` | Similarity threshold (0.0–1.0) |
| `max_memories` | `MEM0_MAX_MEMORIES` | `50` | Max results for list/search |
| `infer` | `MEM0_INFER` | `true` | Enable semantic fact extraction |

## OpenCode Plugin Installation

For one-line installation in OpenCode:

```bash
opencode plugin add opencode-mem0-mcp
```

The plugin automatically registers the mem0 MCP server with your OpenCode configuration.

## License

MIT
