# Design

## Context

See `proposal.md` - Why. Today `mem0_mcp_server.py` hardcodes
`MCPServer(name="mem0-mcp", version="1.0.0")` (line 368), the `mem0_get_status`
tool returns only hub health, `main()` has no `--version`, and `pyproject.toml`
declares the version as a separate static `"1.0.0"`. The value the server
reports and the value the package installs therefore have no relationship.

## Goals / Non-Goals

**Goals:**

- One authoritative version value that every report surface uses.
- The installed package version and the running server's reported version agree.
- A test can read the version from a running server and compare it to an
  expected build.

**Non-Goals:**

- No version reporting for the OpenCode adapter package (it has its own
  `package.json` version and is independent).
- No automatic update checks, build-stamping from git, or changelog.
- No change to hub connection behavior or the `hub-connection` capability.

## Decisions

### Authoritative value is a literal `__version__` in the server module

Add `__version__ = "1.1.0"` as a top-level literal in `mem0_mcp_server.py` and
reference it from `MCPServer(...)`, the status tool, and the CLI.

- Alternative: read the installed distribution with
  `importlib.metadata.version("mem0-mcp-server")`. Rejected as the primary
  source because it fails when the module runs from a source checkout that was
  never installed, and it adds an import-time failure path. The literal always
  works.

### `pyproject.toml` derives its version from that literal

Switch `[project]` to `dynamic = ["version"]` and add
`[tool.setuptools.dynamic] version = { attr = "mem0_mcp_server.__version__" }`.

- This keeps a single source of truth: editing `__version__` updates the
  installed package metadata, so the spec's "reported version equals the
  installed package version" holds.
- setuptools reads a simple top-level string assignment statically, so the
  build does not need to import the module (and its `mcp`/`httpx` imports).

### Report the version on three surfaces

- MCP server metadata: `MCPServer(name="mem0-mcp", version=__version__)`.
- Status tool: add `"server_version": __version__` to the tool's JSON result
  (both the success and error payloads, so the version is readable even when the
  hub is unreachable).
- CLI: `parser.add_argument("--version", action="version",
  version=f"%(prog)s {__version__}")`, which prints and exits `0` without
  loading config, contacting the hub, or starting a transport.

### Bump to `1.1.0`

A version-reporting addition is a backward-compatible feature, so the minor
component increases from `1.0.0` to `1.1.0`.

## Risks / Trade-offs

- [The dynamic `attr:` read could fail if `__version__` stops being a static
  literal at module top level] -> Keep it a plain literal assignment; verify by
  building/installing the package and reading the resulting metadata.
- [The already-installed entry point keeps reporting the old version until it is
  reinstalled] -> Intentional: that is exactly how a test detects a stale
  install. Document the reinstall step in the README and migration plan.
- [Adding `server_version` changes the status tool's payload shape] -> Additive;
  existing consumers that read `status`/`data` are unaffected.

## Migration Plan

1. Change `mem0_mcp_server.py` and `pyproject.toml`.
2. Reinstall to refresh the entry point and metadata:
   `python3 -m pip install --user --break-system-packages .`
3. Verify with `mem0-mcp-server --version` and a `mem0_get_status` call.
4. Rollback: revert the files; the previously installed version still runs.

## Open Questions

None.
