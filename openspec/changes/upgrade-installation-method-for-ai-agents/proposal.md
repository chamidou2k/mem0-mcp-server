# Proposal

## Why

The mem0 MCP server's installation method is currently tied to a single AI agent host (OpenCode): the server is registered through `opencode plugin add` and the setup is documented exclusively for OpenCode. Users of other AI agent hosts — in scope: `opencode` and `pi` — cannot install or register the server through a consistent, documented procedure. Generalizing the installation method lets any supported AI agent host pick up the mem0 server with the same single-specifier, no-build-step install from the project Git repository.

## What Changes

- Generalize the installation/registration procedure so it works for multiple AI agent hosts (`opencode`, `pi`) rather than OpenCode only.
- Document per-agent install steps: OpenCode via `opencode plugin add` from the repo; `pi` via its own installer/registration mechanism.
- Retain the existing install contract: the server installs from the project's Git repository with a single specifier and without a build step; the adapter package stays `private` with no `devDependencies`/`scripts`, and its compiled entry point stays committed and self-contained.
- Add any new per-agent integration under `integrations/` following the existing `integrations/opencode` layout.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `opencode-adapter`: the installation/registration method is extended to support multiple AI agent hosts (`opencode`, `pi`) instead of OpenCode only. The existing requirements (single-specifier repo install, no build step, private package, self-contained committed entry point) are retained; the agent-specific registration steps are generalized per host. No spec-level requirement is removed — only extended to cover additional agent hosts.

## Impact

- `integrations/` directory: currently only `integrations/opencode`; may add a `pi` integration mirroring the opencode layout.
- Installation documentation (README Quick Start and per-agent integration walkthroughs).
- `openspec/specs/opencode-adapter/spec.md` — the installation/registration requirements are extended to cover multiple agent hosts.
- No change to `hub-connection` or `server-version` capabilities (no requirement changes there).
