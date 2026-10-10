# Proposal

## Why

The hub's HTTPS endpoint enforces authentication: requests to `/memories` return `401 Unauthorized` unless they carry an `X-API-Key` header. The MCP server never sends any API-key header today — the configured `api_key` only toggles whether a `Content-Type` header is added — so storing and retrieving memories over HTTPS fail with `401` even when a key is configured.

## What Changes

- When `api_key` is configured (non-empty and not `none`), send it as the `X-API-Key` request header on every request to the mem0 hub, for both the HTTP and HTTPS endpoints.
- When `api_key` is empty or `none`, send no `X-API-Key` header (current behavior preserved).
- Keep the existing `Content-Type`, `X-Mem0-Source`, and `X-Mem0-Client` header behavior unchanged.
- The key value comes from the configuration file's existing `api_key` option (its `MEM0_API_KEY` environment mapping is retained).
- Update `README.md` to document that the API key is sent as `X-API-Key` and is required by hubs that enforce authentication.
- No change to endpoint selection, TLS verification, MCP tools, resources, transports, or the mem0 REST API surface.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hub-connection`: outbound hub requests now carry the configured API key as an `X-API-Key` header when a key is set.

## Impact

- `mem0_mcp_server.py`: `Mem0Client` request-header construction
- `README.md`: configuration documentation for `api_key`
- Dependencies: none added
- Compatibility: hubs that do not require authentication ignore the extra header; when `api_key` is unset or `none`, no header is sent, so existing behavior is unchanged
