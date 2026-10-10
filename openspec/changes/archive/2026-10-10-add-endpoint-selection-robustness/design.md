# Design

## Context

`mem0_mcp_server.py` is a single-file FastMCP server. Its `Mem0Client` currently holds a required HTTP `httpx.AsyncClient` built from `mem0_host` and an optional HTTPS client built from `mem0_host_https` with `verify=cert_path`; `_select_client()` probes HTTP and falls back to HTTPS. `DEFAULT_CONFIG` hardcodes `mem0_host` = `http://192.168.1.100:8001`, and `load_config()` always normalizes `mem0_host`. Endpoint-selection requirements live in `openspec/specs/hub-connection/spec.md`; motivation is in proposal.md.

## Goals / Non-Goals

**Goals:**
- Allow HTTPS to be the only configured endpoint
- Preserve HTTP-only, both-configured (probe/prefer HTTP), and existing fallback behavior
- Treat empty / null / absent as "not configured"
- Start the server when neither endpoint is configured; fail clearly per request

**Non-Goals:**
- Changing how HTTPS certificates are verified (existing `cert_path` rules stay)
- Falling back from HTTPS to HTTP (HTTP remains the only preferred endpoint)
- Health-check TTL caching or background monitoring
- Env-var support for the endpoint options

## Decisions

**1. "Configured" = non-empty after env/file/default merge.**
`None`, `""`, and whitespace-only values are treated as unset. Only configured endpoints are normalized and validated. Alternative: ad-hoc truthiness checks inline — rejected because several call sites need the same rule.

**2. Drop the hardcoded `mem0_host` default.**
`DEFAULT_CONFIG["mem0_host"]` becomes `""` (`mem0_host_https` stays `""`). This makes "HTTP not configured" expressible without the operator fighting a default. Marked BREAKING in the proposal. Alternative: keep the default and require operators to blank it — rejected per user decision.

**3. `Mem0Client` holds optional clients.**
`__init__` builds `self.client` only when an HTTP host is resolved and `self.https_client` only when an HTTPS host is resolved; either may be `None`. `_select_client()` becomes the single selection point with four branches:
- both `None` → raise a clear `RuntimeError` ("no mem0 endpoint configured; set mem0_host or mem0_host_https") so each operation fails while startup still succeeds.
- `https_client is None` → return `client` (HTTP-only, no probe).
- `client is None` → return `https_client` (HTTPS-only, no probe).
- both present → probe HTTP; return `client` on success, else `https_client`.

Alternative: keep one required client — rejected because it cannot represent HTTPS-only or neither.

**4. Failure is per request, not at startup.**
Per user decision, a completely unconfigured server still starts and fails on each operation. `_select_client()` raises before any HTTP call, so the error is deterministic and names the missing options. Alternative: fail fast at startup — rejected by the user.

**5. `cert_path` validation is unchanged.**
Still required and validated (exists/readable) whenever `mem0_host_https` is configured, including HTTPS-only configs. No unverified TLS.

**6. The selection matrix is exhaustive.**
Four cases (HTTP-only, HTTPS-only, both, neither) map to the four `_select_client()` branches, keeping HTTP the only preferred endpoint and HTTPS the only fallback.

## Risks / Trade-offs

- [Removing the built-in default breaks configs that never set `mem0_host`] → Documented in README and marked BREAKING; such configs now fail per request with a message naming the fix.
- [A mis-set empty `mem0_host` silently switches a deployment to HTTPS-only] → Empty-as-unset semantics documented; startup logs the effective endpoints (or the no-endpoint state).
- [Neither-configured server starts and every call errors] → Accepted per user decision; the error names both options.
- [HTTP-only configs gain no probing, so a dead HTTP endpoint is not auto-detected] → Unchanged behavior; there is no configured alternate endpoint to fall back to.

## Migration Plan

1. Deploy; configs that set `mem0_host` explicitly behave as before (HTTP-only or both-configured).
2. Configs relying on the removed default must set `mem0_host` and/or `mem0_host_https`.
3. HTTPS-only: set `mem0_host` to `""` and configure `mem0_host_https` plus `cert_path`.
4. Rollback = revert the code; no data or schema changes.

## Open Questions

None — the empty-as-unset rule, dropped default, and neither-configured behavior were resolved with the user before this design.
