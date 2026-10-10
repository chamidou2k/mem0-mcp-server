# Package the server for simple installation and add the OpenCode adapter

## Why

Installing the server today means cloning the repo, running
`pip install -r requirements.txt`, hand-editing a `config.json`, and launching
`start.sh`. Three problems block simple installation:

- The server has no packaging metadata (`pyproject.toml`, console entry point),
  so it cannot be installed or run with `pip`/`uvx`, and an MCP adapter cannot
  resolve it as a module.
- `start.sh` creates a `.venv` but never installs the dependencies, so it fails
  immediately on a fresh machine.
- The OpenCode adapter (`opencode-mem0-mcp`) lives in a separate, stale
  repository: it forwards only the original eight options (no HTTPS/CA/hostname
  support) and passes its configuration as inline JSON on `--config`, which the
  server treats as a file path and silently ignores.

## What Changes

- Add `pyproject.toml` with the `mem0-mcp-server` package and a
  `mem0-mcp-server` console script so the server is installable and runnable via
  `uvx`/`pip` (for example
  `uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`).
- Fix `start.sh` so the virtual environment it creates also installs
  `requirements.txt`.
- Bring the OpenCode adapter into this repository under `integrations/opencode/`
  as `opencode-mem0-mcp`.
- Extend the adapter's options to the full hub parameter set, adding
  `mem0HostHttps`, `certPath`, and `tlsVerifyHostname`.
- Forward the adapter's options to the server as environment variables instead
  of inline JSON on `--config`, fixing the silent-config-drop bug and relying on
  the env contract delivered by `pass-all-hub-options-via-env`.
- Update the server README (installation) and add an adapter README.

The server's package metadata and README stay agent-agnostic: they do not
mention OpenCode. The adapter is a thin, optional consumer of the server.

## Capabilities

### New Capabilities

- `opencode-adapter`: the OpenCode plugin that registers the mem0 MCP server
  and maps its options (with environment fallbacks) onto the server's
  environment variables.

### Modified Capabilities

(none)

## Impact

- New files: `pyproject.toml`, `integrations/opencode/` (`package.json`,
  `tsconfig.json`, `src/index.ts`, `README.md`).
- Changed files: `start.sh`, `README.md`.
- Depends on `pass-all-hub-options-via-env`: the adapter forwards the HTTPS, CA,
  and hostname options through the environment variables that change introduces.
