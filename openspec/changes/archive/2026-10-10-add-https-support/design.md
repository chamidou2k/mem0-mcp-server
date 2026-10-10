# Design

## Context

`mem0_mcp_server.py` is a single-file FastMCP server whose `Mem0Client` wraps an `httpx.AsyncClient` with `base_url` taken verbatim from the `mem0_host` config value (typically embedding a scheme, e.g. `http://192.168.1.100:8001`). Config comes from `DEFAULT_CONFIG` → JSON file (`load_config`) → `MEM0_*` env overrides. Motivation is in proposal.md; requirements live in `specs/hub-connection/spec.md` (delta in this change). The hub now exposes both an HTTP and an HTTPS endpoint, and the server must prefer HTTP and fall back to HTTPS per operation.

## Goals / Non-Goals

**Goals:**
- Configure both the HTTP (`mem0_host`) and HTTPS (`mem0_host_https`) hub endpoints
- Prefer HTTP; fall back to HTTPS when the per-operation HTTP status check fails, and return to HTTP when it recovers
- Verify the HTTPS endpoint's certificate against an operator-supplied CA file
- Keep existing configs working unchanged (HTTP-only, no fallback)

**Non-Goals:**
- Server-side TLS for the MCP server's own SSE endpoint (stdio/SSE transport stays as-is)
- Mutual TLS / client certificates
- Env-var support for the new options (config-file only)
- Continuous background health monitoring, or caching/TTL for the HTTP availability check
- Rotating or hot-reloading certificates (restart to apply config)

## Decisions

**1. Resolve both endpoints in `load_config`, not in `Mem0Client`.**
`load_config` normalizes the HTTP base URL (`mem0_host`; scheme-less → `http://`) and the optional HTTPS base URL (`mem0_host_https`; scheme-less → `https://`), and validates `cert_path` when the HTTPS endpoint is present. All failure modes surface at startup before the MCP server binds. Alternative: validating inside `Mem0Client.__init__` — rejected because errors could surface after transport startup.

**2. `Mem0Client` holds both endpoints and routes per operation.**
The client keeps the HTTP `httpx.AsyncClient` (from `mem0_host`) and, when `mem0_host_https` is set, a separate HTTPS client built with `httpx.AsyncClient(base_url=<https>, verify=cert_path)`. Each hub operation first checks the HTTP status endpoint; if it succeeds the operation runs over HTTP, otherwise over the HTTPS client. Availability is re-checked every operation, so traffic returns to HTTP automatically once it recovers (HTTP priority). Alternative: a single client with absolute per-request URLs — rejected because `verify` is fixed at client construction, and two clients keep the HTTP path free of TLS kwargs.

**3. Availability probe is the hub status call, checked per operation.**
Per the user's choice, each hub operation is preceded by a literal `mem0_get_status` check over HTTP. This costs one extra status call per operation while HTTP is healthy. Alternative: attempt the real request on HTTP and probe only after failure — rejected by the user's choice; it saves a call but changes when the fallback decision is made.

**4. Fallback trigger and both-down behavior.**
A failed HTTP status check selects the HTTPS endpoint for that operation. If the HTTPS operation then fails, the underlying connection error surfaces to the caller and the server keeps running — startup never aborts because an endpoint is unreachable ("start on HTTPS anyway"). `mem0_get_status` surfaces the connectivity problem to clients.

**5. `cert_path` validation = presence + `os.path.isfile` + readability at startup.**
Required whenever `mem0_host_https` is configured; fail fast with the offending path in the message. Actual TLS handshake failures (bad CA, untrusted hub) surface per-request as connection errors.

**6. Remove the earlier-planned `access_method` selector.**
The two-endpoint HTTP-priority scheme supersedes static scheme selection; keeping both would create two contradictory sources of truth. `mem0_host` remains the HTTP endpoint, and plan text referencing `access_method` is replaced.

## Risks / Trade-offs

- [Extra status call before every hub operation] → Accepted per user choice; the call is bounded by the existing 30s httpx timeout. Revisit with a short TTL cache if it proves costly.
- [HTTP flapping causes repeated fallback churn] → Availability is re-checked per operation; behavior is deterministic and observable via logs and `mem0_get_status`.
- [Wrong/old CA file rejects the HTTPS endpoint] → Startup checks existence only; handshake errors are logged per request and surfaced by `mem0_get_status`.
- [Both endpoints unreachable] → Server still starts; operations fail with connection errors (no unverified TLS, no crash).
- [Certificate expiry requires restart] → Accepted; config reload is out of scope.

## Migration Plan

1. Deploy the code change; existing configs (only `mem0_host`) behave identically as HTTP-only.
2. Operators opt into fallback by adding `mem0_host_https` and `cert_path` to `config.json` and restarting.
3. Rollback = revert the code or remove the two keys; no data or schema changes involved.

## Open Questions

None — priority order, probe timing, both-down behavior, cert semantics, and env-var scope were resolved with the user before this design.
