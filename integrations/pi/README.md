# pi-mem0-mcp

A pi extension that registers the [Mem0 MCP Server](../../) as a local MCP
server named `mem0`, giving pi persistent memory backed by your mem0 hub.

Unlike OpenCode (which loads an adapter plugin), pi registers MCP servers
directly through `pi mcp add <server> -- <command>`. This extension surfaces
the mem0 server specification and default launch command that `pi mcp add`
consumes.

## Setup

The end-to-end path from a bare machine to `mem0` available in pi:

1. **Install `pi`** (the pi coding assistant) if you do not have it:

   ```bash
   # pi installs to ~/.local/bin/pi
   curl -LsSf https://pi.dev/install.sh | sh
   ```

2. **Pre-install the server (recommended).** Installing the server once as a uv
   tool makes every start fast and lock-free:

   ```bash
   uv tool install --force --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server
   ```

3. **Install the pi extension**, straight from this repository:

   ```bash
   pi install 'git:github.com/chamidou2k/mem0-mcp-server#main::path:integrations/pi'
   ```

4. **Register the mem0 MCP server with pi.** pi manages MCP servers through
   `pi mcp add`; run this once to add `mem0` to your MCP servers
   (`~/.pi/agent/mcp.json`):

   ```bash
   pi mcp add mem0 -- uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server
   ```

   To point pi at a pre-installed `mem0-mcp-server` binary instead, override
   the launch command with `serverCommand`:

   ```bash
   pi mcp add mem0 -- /home/you/.local/bin/mem0-mcp-server
   ```

   Hub connection options (`mem0_host`, `api_key`, `cert_path`, …) are passed
   through `MEM0_*` environment variables. Set them in your shell or in
   `~/.pi/agent/mcp.json` via `pi mcp add mem0 --env MEM0_HOST=...`.

5. **Verify** the server is registered and reachable:

   ```bash
   pi mcp list
   ```

   Expect `mem0` to appear with `state: connected` (or `connecting` while it
   starts). A mem0 hub must be reachable for the connection to succeed.

## Configure

pi stores MCP servers in `~/.pi/agent/mcp.json`. Add a `mem0` entry whose
`env` carries the hub options — the mem0 server reads `MEM0_*` environment
variables:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "/home/you/.local/bin/mem0-mcp-server",
      "env": {
        "MEM0_HOST": "http://<mem0-host>:8001",
        "MEM0_HOST_HTTPS": "https://<mem0-host>:8443",
        "MEM0_CERT_PATH": "/path/to/ca-certificate.pem",
        "MEM0_TLS_VERIFY_HOSTNAME": "true",
        "MEM0_API_KEY": "<api-key>",
        "MEM0_USER_ID": "<user-id>",
        "MEM0_AGENT_ID": "<agent-id>",
        "MEM0_CHANNEL": "",
        "MEM0_SEARCH_THRESHOLD": "0.1",
        "MEM0_MAX_MEMORIES": "50",
        "MEM0_INFER": "true"
      }
    }
  }
}
```

Every option is optional. An omitted option falls back to the server's own
default. `command` points at the `mem0-mcp-server` executable — for example
`/home/you/.local/bin/mem0-mcp-server` after `uv tool install`; the default
launch command is `uvx --from git+https://github.com/chamidou2k/mem0-mcp-server
mem0-mcp-server`.

### Options

| Environment variable | Description |
|---|---|
| `MEM0_HOST` | Preferred HTTP hub URL |
| `MEM0_HOST_HTTPS` | HTTPS hub URL (fallback, or HTTPS-only) |
| `MEM0_CERT_PATH` | CA certificate/bundle verifying the HTTPS hub |
| `MEM0_TLS_VERIFY_HOSTNAME` | Verify the hub cert's hostname/IP (default `true`) |
| `MEM0_API_KEY` | API key sent as the `X-API-Key` header |
| `MEM0_USER_ID` | Mem0 user identifier |
| `MEM0_AGENT_ID` | Mem0 agent identifier |
| `MEM0_CHANNEL` | Channel/source identifier |
| `MEM0_SEARCH_THRESHOLD` | Similarity threshold (0.0–1.0) |
| `MEM0_MAX_MEMORIES` | Max results for list/search |
| `MEM0_INFER` | Enable semantic fact extraction |

## Development

The extension ships prebuilt, so installing from Git needs no build. Maintainers
build from the repository root (the build tooling lives in the root manifest):

```bash
npm install
npx tsc -p integrations/pi
```

Commit the regenerated `dist/` whenever `src/` changes.
