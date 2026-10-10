# Design

## Context

OpenCode installs a Git plugin by preparing the repository as a dependency and
then selecting the package named by `::path:`. The preparation step runs a
package install, so it requires a `package.json` at the clone root, and that
install must succeed. The `mem0-mcp-server` repository is a Python project
(`pyproject.toml` at the root), and its adapter package declares
`devDependencies`, so preparation fails and the adapter is never selected.

Verified with throwaway repositories and the real clone:

- Without a root `package.json`, the install fails (`ENOENT ... <clone>/package.json`).
- With a minimal private root `package.json`, `opencode plugin add
  'git+file://...#main::path:integrations/opencode'` succeeds and OpenCode
  caches the **subdirectory** package (`node_modules/foo-opencode-plugin`),
  proving it honors `::path:`.
- With that root manifest but the adapter's `devDependencies` still present, the
  install fails again (`NpmInstallFailedError` / `git dep preparation failed`).
- Removing `devDependencies` from the adapter package makes the install succeed,
  even when the same development dependencies are declared in the root manifest.
- System npm 9.2.0 ignores `::path:` (installs the root package) and bun 1.4.2
  rejects it, but OpenCode's bundled installer supports it. OpenCode is the
  supported installer, so the fix targets it.

## Goals / Non-Goals

- Goal: the documented one-line Git install works.
- Non-Goal: publishing anything to npm; the root manifest is private.
- Non-Goal: changing the Python package or the adapter code.

## Decisions

### Decision: Add a minimal private root `package.json` that carries the dev dependencies

```json
{
  "name": "mem0-mcp-server",
  "version": "1.1.0",
  "private": true,
  "description": "mem0 MCP server and OpenCode adapter",
  "license": "MIT",
  "devDependencies": {
    "@opencode-ai/plugin": "^1.18.34",
    "@opencode/plugin": "^2.0.26",
    "@types/node": "^22.20.5",
    "typescript": "^5.6.0"
  }
}
```

- No `scripts` and no `workspaces`: the manifest exists to satisfy the
  installer's Git preparation step and to host the build-time dependencies for
  maintainers; it must not run side effects.
- `private: true` prevents accidental publication.
- `version` mirrors the Python server version (`mem0_mcp_server.__version__`)
  for human consistency; the file is never published, so drift is cosmetic.
- Alternative rejected: move the adapter to the repository root, which would
  break the server-plus-integrations layout and the Python packaging.
- Alternative rejected: a separate plugin repository, which duplicates the
  server and abandons the single-link install.
- Alternative rejected: keep the root manifest with no `devDependencies`, which
  leaves maintainers without a place to install TypeScript for the adapter build.

### Decision: The adapter package declares no `devDependencies`

`integrations/opencode/package.json` keeps `scripts`, `files`, and the optional
`peerDependencies`, but declares no `devDependencies`. Because `dist/` is
committed, the adapter needs nothing installed at install time, so OpenCode's
Git preparation has nothing to resolve and succeeds. The build-time tooling
(TypeScript, type packages) lives in the root manifest instead, where it is used
by `npm install` at the repository root before building the adapter.

No npm lock files are committed. The adapter ships no dependencies, and a
generated lock embeds a machine-specific registry mirror plus the adapter's peer
tree, which is noise in a Python-first repository.

## Risks / Trade-offs

- A root `package.json` can make tooling treat the repository as a Node project.
  Mitigated by `private: true`, no scripts, and a stray root `node_modules/`
  already being git-ignored.
- Maintainers must `npm install` at the root (not in `integrations/opencode`) to
  get the build tooling; the adapter README documents the build command.
- The install still requires `uv` at runtime and an OpenCode that supports
  `::path:` (documented in the adapter README).

## Migration Plan

Additive. Rollback: delete the root `package.json` and restore the adapter's
`devDependencies`.

## Open Questions

None.
