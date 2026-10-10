# Proposal

## Why

On a machine whose environment defines a proxy variable (for example
`ALL_PROXY=socks5://...`), the server crashes at startup before it can serve
anything. httpx reads the proxy environment, selects a SOCKS transport, and
raises:

```
ImportError: Using SOCKS proxy, but the 'socksio' package is not installed.
Make sure to install httpx using `pip install httpx[socks]`.
```

The process exits immediately, so an MCP client only sees the connection close
(OpenCode reports `Connection closed`). This was hit while installing on macOS;
a Linux host without a proxy variable worked. A self-hosted hub should be
reachable regardless of unrelated ambient proxy settings, so the server must not
fail to start because of them.

## What Changes

- Declare the httpx SOCKS extra (`httpx[socks]`, which installs `socksio`) as a
  runtime dependency so an environment-provided SOCKS proxy no longer aborts
  startup.
- Document proxy behavior: the server honors standard proxy environment
  variables, and a LAN hub can be reached by excluding it via `NO_PROXY`.
- No change to hub endpoints, TLS verification, API-key handling, options, or
  the OpenCode adapter.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `hub-connection`: add a requirement that the server starts and connects
  successfully even when proxy environment variables, including SOCKS proxies,
  are present.

## Impact

- `pyproject.toml` and `requirements.txt`: `httpx>=0.25.0` becomes
  `httpx[socks]>=0.25.0`.
- `README.md`: a short note on proxy environment variables and `NO_PROXY`.
- `mem0_mcp_server.py` is unchanged; the OpenCode adapter and specs for it are
  unchanged.
