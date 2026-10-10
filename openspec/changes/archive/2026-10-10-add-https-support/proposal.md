# Proposal

## Why

The remote mem0 hub service offers both HTTP and HTTPS access. The MCP server should prefer the plain HTTP endpoint and automatically fall back to the HTTPS endpoint when HTTP is unavailable, so deployments keep working during HTTP outages while still allowing encrypted, CA-verified access when needed. Today the server cannot configure a second (HTTPS) endpoint or supply a CA certificate.

## What Changes

- Add a `mem0_host_https` config option naming the hub's HTTPS endpoint; `mem0_host` continues to name the HTTP endpoint.
- Add a `cert_path` config option naming a CA certificate/bundle used to verify the HTTPS endpoint (httpx `verify=`); it is required whenever `mem0_host_https` is configured, failing fast at startup if missing or unreadable.
- Before each hub operation, check HTTP availability via the hub status call: use HTTP when it responds, otherwise use the HTTPS endpoint. HTTP is preferred and re-checked per operation, so traffic returns to HTTP as soon as it recovers. If HTTP is down and no HTTPS endpoint is configured, the underlying request error surfaces.
- Remove the previously planned `access_method` selector — the two-endpoint HTTP-priority scheme supersedes it (plan-only; the option was never implemented).
- Extend `config.template.json` and README configuration documentation with the new options.
- No change to MCP tools, resources, transports, or the mem0 REST API surface.

## Capabilities

### New Capabilities

- `hub-connection`: How the MCP server establishes its outbound connection to the remote mem0 hub — endpoint selection across the configured HTTP and HTTPS endpoints, HTTP-priority fallback, base-URL construction, and TLS certificate verification requirements.

### Modified Capabilities

(none — no existing specs)

## Impact

- `mem0_mcp_server.py`: `DEFAULT_CONFIG`, `load_config()` validation, `Mem0Client` (HTTP + HTTPS base URLs, `httpx.AsyncClient` TLS `verify`, per-operation endpoint selection)
- `config.template.json`: new `mem0_host_https` and `cert_path` keys
- `README.md`: configuration reference table and config example
- Dependencies: none added (`httpx` already supports custom CA bundles via `verify=`)
- Compatibility: existing configs (only `mem0_host`, no new keys) remain HTTP-only and behave unchanged; new options are config-file only (no env-var mappings)
