# Proposal

## Why

The adapter is meant to be installed straight from the project's Git URL
(`opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'`),
but two gaps make that install broken. The compiled `dist/` entry point is
git-ignored and the package has no build-on-install step, so a fresh Git
install has no `main` file. And the adapter launches `mem0-mcp-server` from
`PATH`, so installing only the plugin never provides the Python server. The
goal is a single GitHub specifier that yields a working mem0 MCP server.

## What Changes

- Register the server through `uvx` from the project repository by default
  (`uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`),
  so the plugin install also supplies the server; add an optional `serverCommand`
  override for pinned versions or local development.
- Ship the compiled entry point in the repository: stop ignoring
  `integrations/opencode/dist` and commit the built output so a Git install
  needs no build step.
- Document the one-line GitHub install and the `uv` prerequisite in the adapter
  README, and point at it from the root README.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `opencode-adapter`: the registered server command changes from a bare
  `mem0-mcp-server` to a repository-sourced `uvx` launch with an optional
  override, and the adapter gains a requirement that it is installable from the
  project repository without a separate build step.

## Impact

- `integrations/opencode/src/index.ts` (default command + `serverCommand` option)
- `integrations/opencode/package.json` (version bump)
- `.gitignore` (`dist/` -> `/dist/`) and newly tracked `integrations/opencode/dist/`
- `integrations/opencode/README.md`, root `README.md`
- The Python server and its hub-connection behavior are unchanged.
