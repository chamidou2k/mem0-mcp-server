# Proposal

## Why

The one-line install
`opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'`
still fails. OpenCode prepares the Git dependency by running a package install
for the repository, and the adapter package at `integrations/opencode` declares
lifecycle `scripts` (`build`/`prepare`) that the preparation step tries to run.
The repository is a Python project, so the TypeScript build tool that those
scripts invoke is not present in the prepared checkout; preparation aborts with
`git dep preparation failed`. The archived "installs from the project
repository" requirement is therefore not actually satisfied.

## What Changes

- Add a minimal `package.json` at the repository root, marked `private`, with no
  `scripts`/`workspaces`, that carries the adapter's development dependencies so
  maintainers have a place to install the build tooling.
- Remove the adapter package's `scripts` block from
  `integrations/opencode/package.json` (and its `devDependencies`) so the
  installer's Git preparation has nothing to run; keep its peer declarations and
  committed `dist/`.
- Remove `integrations/opencode/package-lock.json`; the adapter ships no
  dependencies, so a lock file adds nothing and would embed a mirror registry.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `opencode-adapter`: the "installs from the project repository" requirement now
  also requires a root `package.json` and requires the adapter package to
  declare no `devDependencies` and no `scripts`, so preparation runs no build.

## Impact

- New file: `package.json` at the repository root.
- `integrations/opencode/package.json`, and removal of
  `integrations/opencode/package-lock.json`.
- `integrations/opencode/src/index.ts` and the compiled `dist/` are unchanged.
- The Python server and `pyproject.toml` are unchanged.
