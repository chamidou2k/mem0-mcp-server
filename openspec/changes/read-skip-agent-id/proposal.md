# Proposal

## Why

The mem0 hub rejects requests that carry both `user_id` and `agent_id` together (returning HTTP 500, "Expected where to have exactly one operator"), yet the server's read operations send both whenever an `agent_id` is configured. As a result, `mem0_list_memories` and `mem0_get_memory` fail against the hub for every configured deployment, and `mem0_search_memories` filters to a single agent — so an agent configured with a distinct `agent_id` (such as pi) cannot see the user's existing memories. Reads should return the user's full memory store regardless of agent; writes should keep attributing the memory to the configured agent.

## What Changes

- Read operations (`mem0_list_memories`, `mem0_get_memory`, `mem0_search_memories`) stop sending `agent_id` and scope only by `user_id`, so they return the user's full memory store across all agents.
- Write operations (`mem0_add_memory`, `mem0_update_memory`) continue to carry the configured `agent_id` so the hub can attribute new and updated memories.

## Capabilities

### New Capabilities

- `memory-scoping`: defines which hub filter each memory operation uses — writes tag the configured `agent_id`, reads scope only by `user_id` and return the user's whole memory store.

### Modified Capabilities

None. The existing `hub-connection` capability governs endpoint selection, TLS, API key, and proxy — not read/write filtering, which is new behavior.

## Impact

- `mem0_mcp_server.py` — `Mem0Client` methods `add_memory`, `update_memory`, `list_memories`, `get_memory`, `search_memories` (payload/query params for `agent_id`).
- `tests/` — add/update/delete coverage for read/write agent_id filtering.
- `openspec/specs/memory-scoping/spec.md` — new capability created at archive.
- No change to `hub-connection`, `opencode-adapter`, or `server-version`.
