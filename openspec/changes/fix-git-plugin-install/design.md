# Design

## Context

OpenCode installs a Git plugin by preparing the repository as a dependency and
then selecting the package named by `::path:`. The preparation step runs a
package install at the clone root, so it requires a `package.json` there. The
`mem0-mcp-server` repository is a Python project (`pyproject.toml` at the root),
so preparation fails and the adapter is never selected.

Verified with a throwaway repository at `/tmp/opencode/ghinstall-test/repo`:

- Without a root `package.json`, the install fails (`ENOENT ... <clone>/package.json`).
- With a minimal private root `package.json`, `opencode plugin add
  'git+file://...#main::path:integrations/opencode'` succeeds and OpenCode
  caches the **subdirectory** package (`node_modules/foo-opencode-plugin`),
  proving it honors `::path:`.
- System npm 9.2.0 ignores `::path:` (installs the root package) and bun 1.4.2
  rejects it, but OpenCode's bundled installer supports it. OpenCode is the
  supported installer, so the fix targets it.

## Goals / Non-Goals

- Goal: the documented one-line Git install works.
- Non-Goal: publishing anything to npm; the root manifest is private.
- Non-Goal: changing the Python package or the adapter code.

## Decisions

### Decision: Add a minimal private root `package.json`

```json
{
  "name": "mem0-mcp-server",
  "version": "1.1.0",
  "private": true,
  "description": "mem0 MCP server and OpenCode adapter",
  "license": "MIT"
}
```

- No `scripts` and no `workspaces`: the manifest exists only to satisfy the
  installer's Git preparation step, and running it must have no side effects.
- `private: true` prevents accidental publication.
- `version` mirrors the Python server version (`mem0_mcp_server.__version__`)
  for human consistency; the file is never published, so drift is cosmetic.
- Alternative rejected: move the adapter to the repository root, which would
  break the server-plus-integrations layout and the Python packaging.
- Alternative rejected: a separate plugin repository, which duplicates the
  server and abandons the single-link install.

## Risks / Trade-offs

- A root `package.json` can make tooling treat the repository as a Node project.
  Mitigated by `private: true`, no scripts, and no dependencies; a stray root
  `node_modules/` is already git-ignored.
- The install still requires `uv` at runtime and an OpenCode that supports
  `::path:` (documented in the adapter README).

## Migration Plan

Additive. Rollback: delete the root `package.json`.

## Open Questions

None.
