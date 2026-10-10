# Proposal

## Why

The one-line install
`opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'`
still fails. OpenCode prepares the Git dependency by running a package install
at the repository root, and the root has no `package.json` (this is a Python
repo with `pyproject.toml`), so preparation aborts before OpenCode can select the
`integrations/opencode` subdirectory through `::path:`. The previously archived
"installs from the project repository" requirement is therefore not actually
satisfied.

## What Changes

- Add a minimal `package.json` at the repository root, marked `private` and with
  no `scripts`/`workspaces`, so the installer's Git preparation step succeeds.
  It does not publish anything and does not affect the Python package.
- Keep the adapter package at `integrations/opencode` selected via the
  documented `::path:integrations/opencode` selector.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `opencode-adapter`: the "installs from the project repository" requirement now
  also requires a root `package.json` so the Git dependency preparation step
  succeeds.

## Impact

- New file: `package.json` at the repository root.
- `integrations/opencode/src/index.ts` and the compiled `dist/` are unchanged.
- The Python server and `pyproject.toml` are unchanged.
