# Design

## Context

The mem0 hub rejects a request that carries both `user_id` and `agent_id` (HTTP 500: "Expected where to have exactly one operator"), while the server currently sends both on every operation where `agent_id` is set (which is always, since `agent_id` defaults to a non-empty value). This breaks `mem0_list_memories` and `mem0_get_memory` against the hub and makes `mem0_search_memories` filter to a single agent, so an agent configured with a distinct `agent_id` cannot see the user's existing memories. See `proposal.md - Why` for motivation; see the `memory-scoping` spec delta for the requirements this design satisfies.

## Goals / Non-Goals

**Goals:**
- Read operations (`list_memories`, `get_memory`, `search_memories`) send only `user_id`, so they return the user's full memory store across all agents.
- Write operations (`add_memory`, `update_memory`) keep sending the configured `agent_id` for hub attribution.
- No hub-side changes are required — the fix is entirely in the request parameters the server sends.

**Non-Goals:**
- Changing endpoint selection, TLS, API key, or proxy behavior (`hub-connection`).
- Changing how memories are stored server-side (the server holds no persistent state).
- Supporting arbitrary per-agent read filters (reads intentionally ignore `agent_id`).

## Decisions

- **Drop `agent_id` from read requests, keep `user_id`**: `list_memories` and `get_memory` build their query params from `user_id` only; `search_memories` sends `query` and `user_id` only. This satisfies the hub's single-operator constraint and returns all agents' memories for the user. Alternative considered: sending neither filter (hub-wide search) — rejected, as it would cross users.
- **Keep `agent_id` on write requests**: `add_memory` continues to include `agent_id` in its payload; `update_memory` SHALL include `agent_id` so updates remain attributable. Alternative considered: dropping `agent_id` from updates too — rejected, because writes must stay attributable to an agent.
- **New capability `memory-scoping`**: the read/write filter contract is a durable system behavior with no current owner, so it gets its own spec rather than being folded into `hub-connection` (which governs endpoint/TLS/key concerns).

## Risks / Trade-offs

- [The hub's update endpoint may not accept `agent_id`] → Verified against the running hub: `PUT /memories/{id}` accepts `agent_id` (a request with it and without it both reach the "memory not found" path, so the parameter is not rejected). `update_memory` can therefore carry it.
- [Reads now return every agent's memories] → An agent configured with `agent_id=pi` will see OpenCode's memories too. This is the intended shared-memory behavior, but callers that expected per-agent isolation must be aware.
- [Doc/code default mismatch on `agent_id`] → Code defaults to `"opencode"`, README documents `"agent"`; unrelated to this change but worth noting when verifying requests.

## Migration Plan

No migration: the change only alters request parameters. Rollback is reverting the `Mem0Client` method changes; existing memories are unaffected.

## Open Questions

None.
