# Proposal

## Why

The hub can be reached over HTTP and/or HTTPS, but the current server always treats `mem0_host` as the HTTP endpoint (with a built-in default) and `mem0_host_https` only as an optional fallback. An HTTPS-only deployment is impossible, and the built-in default means an HTTP endpoint is always implied even when the operator does not configure one. The server should adapt to whichever endpoints are actually configured.

## What Changes

- Treat an endpoint as **configured only when its option has a non-empty value**: empty string, `null`, or an absent key means "not configured".
- Endpoint selection behavior:
  - HTTP configured only → use HTTP (no probing).
  - HTTPS configured only → use HTTPS (no probing).
  - Both configured → check HTTP per operation, prefer HTTP, fall back to HTTPS when HTTP is unavailable.
  - Neither configured → the server still starts; each hub operation fails with a clear "no endpoint configured" error.
- **BREAKING**: remove the built-in `mem0_host` default (`http://<hub>:8001`). Operators must configure at least one of `mem0_host` or `mem0_host_https`; a deployment that previously relied on the implicit default now fails per request until an endpoint is set.
- Update `config.template.json` and README to document that leaving `mem0_host` empty while setting `mem0_host_https` (and `cert_path`) enables HTTPS-only access.
- No change to MCP tools, resources, transports, or the mem0 REST API surface.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hub-connection`: endpoint selection now supports an unset HTTP endpoint (HTTPS-only) and the unset-both case (per-request failure), and no longer depends on a built-in HTTP default.

## Impact

- `mem0_mcp_server.py`: `DEFAULT_CONFIG` (remove the hardcoded `mem0_host` default), `load_config()` (treat empty/null as unset; normalize and validate only configured endpoints), `Mem0Client` (optional HTTP and HTTPS clients, expanded selection logic)
- `config.template.json`: ensure the empty-as-unset semantics are represented
- `README.md`: document the four endpoint-selection cases
- Tests: update config tests for the removed default; add HTTPS-only and neither-configured fallback tests
- Dependencies: none
- Compatibility: configs that explicitly set `mem0_host` are unaffected; configs relying on the removed built-in default fail per request until an endpoint is configured
