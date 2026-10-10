# Design

## Context

See proposal.md for motivation. In `Mem0Client.__init__` a `headers` dict is built once and shared by both the HTTP and HTTPS `httpx.AsyncClient` instances: `Content-Type` is added only when `api_key != "none"`, `X-Mem0-Source` is set when `channel` is configured, and `X-Mem0-Client: mem0-mcp` is always sent. The hub's HTTPS `/memories` endpoint requires an `X-API-Key` header (verified empirically: `X-API-Key` → 200; `Authorization: Bearer`/`Token` or no header → 401); `/health` is open. Requirements are in `specs/hub-connection/spec.md`.

## Goals / Non-Goals

**Goals:**
- Authenticate hub requests using the configured API key via the `X-API-Key` header
- Preserve existing behavior when no key is configured
- Cover both the HTTP and HTTPS endpoints with one change

**Non-Goals:**
- Introducing a new configuration option (the existing `api_key` is reused)
- Changing how the key is supplied (still the config file `api_key`, with the existing `MEM0_API_KEY` env mapping)
- Mutual TLS, OAuth, token refresh/rotation
- Enforcing HTTPS in code when a key is present

## Decisions

**1. Reuse the existing `api_key` config value (user decision).**
No new option; the value continues to come from the config file, and the existing `MEM0_API_KEY` environment mapping is unchanged.

**2. Add `X-API-Key` to the shared `headers` dict in `Mem0Client.__init__`.**
Because the same dict is passed to both clients, adding it once covers HTTP and HTTPS. Condition mirrors the current `Content-Type` toggle: send the header when `api_key` is non-empty and not the literal `none`.

**3. Keep all existing header behavior unchanged.**
`Content-Type`, `X-Mem0-Source`, and `X-Mem0-Client` are untouched.

**4. The literal `none` (and empty) means "no key".**
This preserves backward compatibility with hubs that do not require auth (for example the HTTP endpoint on `:8001`).

**5. Document the cleartext-transport caveat.**
Sending a key over plain HTTP exposes it on the wire; README recommends HTTPS (with certificate verification) when a key is configured. Documentation only — no code enforcement, since the operator may have a trusted/protected network.

Alternative considered: a dedicated `api_key_header` option — rejected; the hub's header name (`X-API-Key`) is fixed and the extra knob adds no value.

## Risks / Trade-offs

- [Key sent in cleartext over HTTP] → Documented; HTTPS recommended when a key is used. Default `none` sends nothing.
- [Hub expecting a different auth scheme] → Verified empirically: `X-API-Key` returns 200 while `Bearer`/`Token` return 401.
- [Header also sent to `/health`] → Harmless and keeps the wiring consistent.

## Migration Plan

1. Deploy the code change; configs with `api_key` set to `none`/empty behave exactly as before (no header).
2. Operators with a real key begin authenticating automatically; recommend pairing with the HTTPS endpoint.
3. Rollback = revert the code or set `api_key` back to `none`.

## Open Questions

None — the header name was confirmed against the live hub and the key source was chosen by the user.
