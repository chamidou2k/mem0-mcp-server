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

### 1. Install

Install the server as a Python package, which provides the `mem0-mcp-server` command:

```bash
pip install .
```

Or run it without installing, straight from the source repository:

```bash
uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server
```

For a plain source checkout without packaging, install the runtime dependencies directly:

```bash
pip install -r requirements.txt
```

Or use the provided start script, which creates a virtual environment, installs the dependencies, and launches the server:

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
  "mem0_host_https": "https://<mem0-host>:<https-port>",
  "cert_path": "/path/to/ca-certificate.pem",
  "tls_verify_hostname": true,
  "api_key": "<api_key>",
  "user_id": "<user_id>",
  "agent_id": "<agent_id>",
  "channel": "<channel>",
  "search_threshold": 0.1,
  "max_memories": 50,
  "infer": true
}
```

The endpoint you configure determines how the server connects:

- **HTTP only** (`mem0_host` set, `mem0_host_https` empty): operations go to HTTP directly.
- **HTTPS only** (`mem0_host` empty, `mem0_host_https` set): operations go to HTTPS directly; `cert_path` is required.
- **Both** (both set): the server checks HTTP availability before each operation and uses HTTPS only when HTTP is unavailable — HTTP is preferred and re-checked every operation, so traffic returns to HTTP as soon as it recovers.
- **Neither** (both empty): the server still starts, but each operation fails with an error until you set `mem0_host` or `mem0_host_https`.

An empty or null value means "not configured". `mem0_host` has no built-in default, so set `mem0_host`, `mem0_host_https`, or both.

**HTTPS certificate verification:** by default the hub's certificate is verified against `cert_path`, including a match of the host/IP you connect to. If the hub uses a self-signed certificate whose name does not match its address (for example `CN=localhost` while connecting to `192.168.1.100`), set `"tls_verify_hostname": false` to keep verifying the certificate chain against `cert_path` while skipping only the hostname/IP match — chain verification is never disabled. This weakens protection against a mismatched or spoofed certificate, so the safer alternative is to add the hub's IP/hostname as a SAN to its certificate and leave the option at `true`.

**API key:** when `api_key` is configured (a non-empty value other than `none`), the server sends it as an `X-API-Key` header on every hub request, for both the HTTP and HTTPS endpoints. `none` or an empty value sends no key header, which keeps hubs that do not require authentication working. Because the key is sent in cleartext over plain HTTP, use the HTTPS endpoint when the hub requires a key.

Or use environment variables (`MEM0_HOST`, `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, `MEM0_TLS_VERIFY_HOSTNAME`, `MEM0_USER_ID`, `MEM0_AGENT_ID`, `MEM0_API_KEY`, `MEM0_CHANNEL`, `MEM0_SEARCH_THRESHOLD`, `MEM0_MAX_MEMORIES`, `MEM0_INFER`). Every option can be set from the environment; an environment variable takes precedence over the same key in the configuration file, and an unset variable leaves the file value (or the default) in place. `MEM0_TLS_VERIFY_HOSTNAME` accepts `true`/`false` (case-insensitive).

### 3. Run

```bash
# Using start script (creates .venv automatically)
./start.sh

# Or directly
python mem0_mcp_server.py --config config.json

# SSE mode (network-accessible)
python mem0_mcp_server.py --config config.json --transport sse --port 8050
```

## Checking the version

The running server reports a single version through every surface (currently
`1.1.0`):

- **CLI:** `mem0-mcp-server --version` (or `python mem0_mcp_server.py --version`)
  prints the version and exits `0` without loading configuration or contacting
  the hub.
- **Status tool:** the `mem0_get_status` tool includes `server_version` in its
  JSON result (on both success and error), so a connected client can confirm
  which build is running.

All surfaces report the same value, which also matches the installed
`mem0-mcp-server` package version. After upgrading, reinstall the package
(`pip install .`) so the installed version and the CLI agree.

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
| `mem0_host` | `MEM0_HOST` | *(unset)* | Mem0 platform HTTP URL (preferred endpoint when set) |
| `mem0_host_https` | `MEM0_HOST_HTTPS` | *(unset)* | Optional HTTPS hub URL, used as fallback when HTTP is unavailable |
| `cert_path` | `MEM0_CERT_PATH` | *(unset)* | CA certificate/bundle verifying the HTTPS hub; required when `mem0_host_https` is set |
| `tls_verify_hostname` | `MEM0_TLS_VERIFY_HOSTNAME` | `true` | Verify the HTTPS hub cert's hostname/IP; set `false` to skip the hostname match while still verifying the chain against `cert_path` |
| `api_key` | `MEM0_API_KEY` | `none` | API key sent as the `X-API-Key` header; `none`/empty sends no key (use HTTPS when a key is required) |
| `user_id` | `MEM0_USER_ID` | `user` | Mem0 user identifier |
| `agent_id` | `MEM0_AGENT_ID` | `agent` | Mem0 agent identifier |
| `channel` | `MEM0_CHANNEL` | `` | Channel/source identifier |
| `search_threshold` | `MEM0_SEARCH_THRESHOLD` | `0.1` | Similarity threshold (0.0–1.0) |
| `max_memories` | `MEM0_MAX_MEMORIES` | `50` | Max results for list/search |
| `infer` | `MEM0_INFER` | `true` | Enable semantic fact extraction |

## Client Integrations

Integrations that register this server with specific MCP clients live under `integrations/`.

## License

MIT
