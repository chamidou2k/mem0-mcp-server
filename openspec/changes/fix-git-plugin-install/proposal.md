# Proposal

## Why

The one-line install
`opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'`
still fails. OpenCode prepares the Git dependency by running a package install
for the repository, and two things break that preparation: the repository root
has no `package.json` (this is a Python repo with `pyproject.toml`), and the
adapter package at `integrations/opencode` declares `devDependencies` that the
preparation step tries to install and cannot complete. The archived "installs
from the project repository" requirement is therefore not actually satisfied.

## What Changes

- Add a minimal `package.json` at the repository root, marked `private`, with no
  `scripts`/`workspaces`, that carries the adapter's development dependencies so
  the installer's Git preparation step succeeds.
- Remove `devDependencies` from `integrations/opencode/package.json` so the
  adapter ships with no install-time dependencies; keep its `scripts`, peer
  declarations, and committed `dist/`.
- Remove `integrations/opencode/package-lock.json`; the adapter ships no
  dependencies, so a lock file adds nothing and would embed a mirror registry.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `opencode-adapter`: the "installs from the project repository" requirement now
  also requires a root `package.json` and requires the adapter package to
  declare no `devDependencies`.

## Impact

- New file: `package.json` at the repository root.
- `integrations/opencode/package.json`, and removal of
  `integrations/opencode/package-lock.json`.
- `integrations/opencode/src/index.ts` and the compiled `dist/` are unchanged.
- The Python server and `pyproject.toml` are unchanged.
