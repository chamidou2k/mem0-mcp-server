# Add server version information

## Why

There is no way to tell which build of the server is actually running. The MCP
server version is hardcoded and never surfaced to clients: the `mem0_get_status`
tool reports only hub health, and the installed `mem0-mcp-server` entry point
gives no version output. After an upgrade (for example reinstalling the package
that the OpenCode adapter launches) a test cannot confirm the new build is the
one in use, which makes verifying an upgrade ambiguous.

## What Changes

- Introduce a single source of truth for the server version (`__version__` in
  `mem0_mcp_server.py`) and use it everywhere the version is reported, instead
  of a hardcoded string.
- Report the running server version through the MCP server metadata
  (`MCPServer(name="mem0-mcp", version=__version__)`).
- Include the server version in the `mem0_get_status` tool output so a client or
  test can read it directly.
- Add a `--version` CLI flag that prints the version and exits.
- Derive the `pyproject.toml` package version from the same single source, so
  `pip`/`uvx` metadata and the running server agree.
- Document how to check the version in the README.
- Bump the version to `1.1.0` for this addition.

## Capabilities

### New Capabilities

- `server-version`: the server exposes its own version consistently — through
  the MCP server metadata, the status tool, the CLI, and its package metadata —
  so clients and tests can identify the running build.

### Modified Capabilities

(none)

## Impact

- Changed files: `mem0_mcp_server.py` (version constant, `MCPServer` version,
  status tool output, `--version` flag), `pyproject.toml` (dynamic version),
  `README.md` (how to check the version), `tests/` (version assertions).
- No change to hub connection behavior or the OpenCode adapter.
