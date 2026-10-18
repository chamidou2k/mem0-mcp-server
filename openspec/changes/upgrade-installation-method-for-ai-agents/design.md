# Design

## Context

The mem0 MCP server currently installs via `pip install .` or `uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`, and registers with OpenCode through `opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'`. Per-agent integration walkthroughs live under `integrations/opencode/`. The `opencode-adapter` capability (spec-driven) governs how the adapter installs and registers the `mem0` stdio MCP server. See `proposal.md - Why` for motivation; see the `opencode-adapter` spec delta for the requirements this design must satisfy.

## Goals / Non-Goals

**Goals:**
- A single, repository-specifier install works for both supported AI agent hosts (`opencode`, `pi`).
- The server install contract is unchanged: install from the project Git repository with a single specifier and no build step; package stays `private` with no `devDependencies`/`scripts`; committed self-contained entry point.
- Per-agent registration steps are documented beside the code under `integrations/<agent>/`.

**Non-Goals:**
- Changing the mem0 server's core behavior, hub connection (`hub-connection`), or version reporting (`server-version`).
- Supporting AI agent hosts beyond `opencode` and `pi` in this change.
- Changing how the OpenCode V1/V2 plugin API works (remains as specified).

## Decisions

- **Generalize `opencode-adapter` registration across agent hosts**: instead of hardcoding OpenCode, the registration requirement names supported agent hosts (`opencode`, `pi`) and leaves the per-host selection to the installation/registration procedure. Alternative considered: a new broad `multi-agent-installation` capability — rejected as a catch-all name that does not name a durable system behavior (proposal guidance).
- **Per-agent integration directories**: add `integrations/pi/` mirroring the `integrations/opencode/` layout rather than nesting agent steps inside the OpenCode adapter. Keeps each host's setup self-contained and discoverable.
- **Server install contract unchanged**: `uvx --from git+...` default launch, `serverCommand` override, no build step — no spec delta needed for these.

## Risks / Trade-offs

- [pi registration command not yet pinned] → The spec keeps the pi scenario behavior-level (`installed and registered with pi from the repository specifier`) so it does not block planning. Define the exact pi CLI/package specifier when writing the `integrations/pi` walkthrough and the implementation tasks; this does not change the spec or task structure.
- [Two agent hosts diverge in registration steps] → Document each host separately under `integrations/<agent>/`; keep specs behavior-level so a host-specific change does not require a spec revision.

## Migration Plan

Existing OpenCode install steps are unchanged (no migration needed for current users). Add the `pi` installation/registration steps alongside them. Rollback: remove `integrations/pi/` and revert the `opencode-adapter` spec delta; OpenCode users are unaffected.

## Open Questions

- Exact pi CLI/package specifier used to register the adapter (implementation detail; does not change the spec or task breakdown — fill in when authoring `integrations/pi` and the tasks).
