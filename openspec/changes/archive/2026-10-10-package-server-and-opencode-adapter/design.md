# Design

## Context

- The server is a single-file stdio/SSE bridge that is currently not
  installable as a package, and `start.sh` creates a virtual environment but
  never installs the dependencies.
- The OpenCode adapter existed in a separate repository
  (`github.com/chamidou2k/opencode-mem0-mcp`) and is stale: it lacks the HTTPS,
  CA, and hostname options and passes configuration in a way the current server
  ignores.
- The env contract for every hub option is delivered by the sibling change
  `pass-all-hub-options-via-env`.
- OpenCode plugins are npm packages loaded via `opencode plugin add`. A plugin
  default-exports a `PluginModule` (`{ id, server }`) and registers a local
  stdio MCP server by mutating `config.mcp` from its `config` hook (SDK
  `McpLocalConfig`), forwarding the server `environment`.

## Goals / Non-Goals

### Goals

- Installation of the server without cloning or hand-managing a virtualenv
  (`uvx`/`pip`).
- A working OpenCode adapter that exposes the full hub parameter set through
  plugin options.
- Keep the server package metadata and README agent-agnostic.

### Non-Goals

- Publishing to PyPI or the npm registry (git-based installation is enough for
  now).
- Changing hub-connection behavior beyond environment support (owned by the
  sibling change).
- Supporting MCP clients other than OpenCode in this change.

## Decisions

### Monorepo layout: server root + `integrations/opencode`

The adapter depends on the server, never the reverse. Keeping both in one
repository lets a single change update and version them together and avoids
cross-repository drift, while the server remains independently installable and
the adapter publishes from its subdirectory. The server package and README do
not mention OpenCode.

### Package the server with `pyproject.toml` and a console script

Add a `mem0-mcp-server` package with the entry point
`mem0-mcp-server = mem0_mcp_server:main`, installable and runnable via
`uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`
or `pip install`.

### Adapter forwards options as environment variables

The adapter maps its options onto the `MEM0_*` environment variables introduced
by `pass-all-hub-options-via-env`. Environment is the cross-client contract and
keeps secrets out of files. This also removes the old inline-JSON-on-`--config`
bug, since the current server treats `--config` as a file path.

### Register the server through the plugin `config` hook

`@opencode-ai/plugin` has no `ctx.mcp.register`. The adapter default-exports a
`PluginModule` (`{ id: "opencode-mem0-mcp", server }`); `server` returns a
`config` hook that sets `config.mcp["mem0"] = { type: "local",
command: ["mem0-mcp-server"], environment: {...}, enabled: true }`. Plugin
options arrive as the second element of OpenCode's `plugin` tuple and are merged
with the `MEM0_*` environment fallback.

### Omit unset options instead of injecting adapter defaults

The old adapter injected its own defaults (`"user"`/`"agent"`), which diverged
from the server's defaults. The adapter now sets only the options that are
configured, so the server's `DEFAULT_CONFIG` stays the single source of
defaults.

### Fix `start.sh` to install dependencies

Run `pip install -r requirements.txt` inside the virtual environment `start.sh`
creates, so a fresh clone works.

## Risks / Trade-offs

- The plugin API is verified against `@opencode-ai/plugin` v1.18.34: the adapter
  default-exports `{ id, server }` and its `server` returns a `config` hook that
  sets `config.mcp["mem0"] = { type: "local", command: [...], environment: {...} }`.
  `McpLocalConfig.environment` carries the `MEM0_*` values to the spawned server.
- `tls_verify_hostname` becomes settable through plugin options and the
  environment, relaxing a previously configuration-file-only control. Chain
  verification against `cert_path` remains mandatory server-side.
- Publishing requires PyPI/npm accounts; git-based installation avoids this for
  now.
- Moving the adapter supersedes the old standalone repository; its users need a
  redirect or deprecation note.

## Migration Plan

- Additive: new `pyproject.toml`, new `integrations/opencode/` directory, README
  updates, and the `start.sh` fix.
- Supersede the old adapter repository with a deprecation/redirect note (out of
  scope here).
- Rollback: remove `pyproject.toml` and `integrations/`, and revert `start.sh`
  and `README.md`.

## Open Questions

- Resolved: the adapter registers the MCP server through the `config` hook
  (`config.mcp["mem0"]` of type `local` with an `environment` map) rather than a
  `ctx.mcp.register` call, which does not exist in `@opencode-ai/plugin`
  v1.18.34.
