# Design

## Context

See `proposal.md` - Why for the failure. The relevant mechanism:

- `Mem0Client.__init__` builds an `httpx.AsyncClient`, which by default reads the
  process proxy environment (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and their
  lowercase forms).
- When that environment names a SOCKS proxy, httpx selects a SOCKS transport,
  which requires the optional `socksio` package.
- The project depends on plain `httpx`, so `socksio` is absent and construction
  raises `ImportError`, aborting the process during startup - before any
  stdio/SSE server is established.

## Goals / Non-Goals

**Goals:**

- The server starts and serves requests regardless of unrelated proxy variables
  in the environment.
- Behavior on hosts without proxy variables is unchanged.
- Environments that genuinely need a proxy keep working.

**Non-Goals:**

- Adding a dedicated proxy configuration option.
- Changing hub endpoints, TLS verification, or API-key handling.
- Disabling ambient proxy support entirely.
- npm publishing.

## Decisions

### Decision: Declare the httpx SOCKS extra instead of disabling environment proxies

Depend on `httpx[socks]` (installs `socksio`) so a SOCKS proxy in the
environment is usable rather than fatal. This is the smallest change that
preserves httpx's documented behavior and keeps proxy-free hosts identical.

Alternative considered: pass `trust_env=False` to the `httpx` clients so the
server ignores proxy variables. Rejected because it silently disables proxies
for users who need one to reach a remote hub, and it diverges from httpx's
defaults. The failure here is a missing optional dependency, not unwanted proxy
behavior.

### Decision: Rely on the standard proxy environment, with `NO_PROXY` for bypass

No new option is introduced. httpx already honours `NO_PROXY`/`no_proxy`, so a
self-hosted LAN hub can be excluded by setting `NO_PROXY` to its host. Adding a
project-specific proxy option would duplicate a well-understood convention.

### Decision: Fix in packaging plus documentation; no server code change

The change is confined to `pyproject.toml` and `requirements.txt` (the extra)
and a README note. `mem0_mcp_server.py` needs no edit, so the fix is
agent-agnostic and applies equally to direct runs, `uv tool install`, and the
OpenCode adapter.

## Risks / Trade-offs

- A proxy that cannot reach the hub now yields connect failures rather than a
  crash → Mitigation: document `NO_PROXY`; the operator controls the
  environment.
- The extra pulls in `socksio`, a small pure-Python dependency → Acceptable;
  it only activates when a SOCKS proxy is configured.

## Migration Plan

Additive. Install the updated package (or `uv tool install --force ...`) and the
startup crash is resolved. Rollback: drop the extra; hosts without a SOCKS
proxy are unaffected either way.
