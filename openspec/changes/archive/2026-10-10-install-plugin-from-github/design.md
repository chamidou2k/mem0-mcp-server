# Design

## Context

The adapter lives at `integrations/opencode/` in the `mem0-mcp-server` repository
and is published as the npm package `opencode-mem0-mcp`. OpenCode V2 installs
plugins from npm-compatible Git specifications and supports npm's
`::path:<subdir>` selector, so the intended install is:

```
opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'
```

Two facts make that install fail today:

- `integrations/opencode/dist/` is git-ignored and the package only has a
  `prepublishOnly` build script. A Git install resolves the package's `main`
  (`./dist/index.js`) with no build step, so the entry point is missing.
- The adapter registers the server with `command: ["mem0-mcp-server"]`, which
  must already be on `PATH`. The Python package is separate, so a plugin-only
  install registers a command that does not exist.

## Goals / Non-Goals

- Goal: one GitHub specifier installs the plugin, and the plugin provides a
  working mem0 MCP server without a separate manual Python install.
- Non-Goal: changing the Python server or its hub-connection behavior.
- Non-Goal: publishing to npm or the MCP registry (deferred).

## Decisions

### Decision: Launch the server through `uvx` from the repository

The default command becomes:

```
["uvx", "--from", "git+https://github.com/chamidou2k/mem0-mcp-server", "mem0-mcp-server"]
```

`uvx` resolves and runs the Python entry point from the same repository on
demand, so installing the plugin alone yields a working server.

- Alternative rejected: keep `["mem0-mcp-server"]` and document a separate
  `pipx install`. That is two steps and not "give the GitHub link".
- Trade-off: requires `uv` on the host, and `uvx` may re-resolve the
  repository on run. The README documents the `uv` prerequisite, and the
  override below lets a user pin a commit or use an installed copy.

### Decision: Optional `serverCommand` option

A `serverCommand` plugin option (a string or an array of strings) overrides the
default. A bare string is normalized to a one-element command array. This
supports pinned versions (`...@<sha>`), local development
(`uvx --from /path/to/repo mem0-mcp-server`), and hosts that already have
`mem0-mcp-server` installed.

### Decision: Commit the compiled entry point instead of building on install

Un-ignore `integrations/opencode/dist/` (change `.gitignore` `dist/` -> `/dist/`,
scoping the ignore to the repository root) and commit the built output. A Git
install then needs no build, which is deterministic and does not depend on a
package manager running lifecycle scripts.

- Alternative rejected: add a `prepare` script. OpenCode's Git install is not
  guaranteed to run `prepare` with devDependencies available, and the build
  needs TypeScript.
- Trade-off: build artifacts are tracked in git and must be rebuilt and
  re-committed when the source changes.

## Risks / Trade-offs

- `uv` missing on the host -> `uvx` cannot launch the server. Mitigated by the
  documented prerequisite and the `serverCommand` override.
- Tracked build output can drift from `src/`. Mitigated by rebuilding before
  each commit (the verification task builds and re-checks).
- The GitHub specifier installs the default branch unless a tag/commit is given;
  users wanting reproducibility can pin `#<sha>`.

## Migration Plan

Additive. Existing users who already have `mem0-mcp-server` on `PATH` can set
`serverCommand` to `"mem0-mcp-server"` to keep current behavior. Rollback:
revert the source change, restore the `dist/` ignore, and re-publish.

## Open Questions

None.
