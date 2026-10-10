# Tasks

## 1. Server packaging

- [x] 1.1 Add `pyproject.toml` declaring the `mem0-mcp-server` package (build backend, runtime dependencies `mcp>=0.3.0` and `httpx>=0.25.0`) and a console script `mem0-mcp-server = mem0_mcp_server:main`. Verify `pip install .` (or `uvx --from . mem0-mcp-server --help`) resolves and runs the entry point.
- [x] 1.2 Fix `start.sh` to install dependencies: run `pip install -r requirements.txt` inside the `.venv` it creates. Verify a fresh clone can launch the server.

## 2. OpenCode adapter

- [x] 2.1 Create `integrations/opencode/` as the `opencode-mem0-mcp` npm package (`package.json`, `tsconfig.json`, `src/index.ts`) that registers a stdio MCP server named `mem0` through the plugin `config` hook (`config.mcp["mem0"]`) launching the installed `mem0-mcp-server`.
- [x] 2.2 Forward every hub option as an environment variable (`mem0Host`→`MEM0_HOST`, `mem0HostHttps`→`MEM0_HOST_HTTPS`, `certPath`→`MEM0_CERT_PATH`, `tlsVerifyHostname`→`MEM0_TLS_VERIFY_HOSTNAME`, `apiKey`→`MEM0_API_KEY`, `userId`→`MEM0_USER_ID`, `agentId`→`MEM0_AGENT_ID`, `channel`→`MEM0_CHANNEL`, `searchThreshold`→`MEM0_SEARCH_THRESHOLD`, `maxMemories`→`MEM0_MAX_MEMORIES`, `infer`→`MEM0_INFER`), with environment fallback and no inline JSON on `--config`. Pass the environment through the plugin `config` hook's `config.mcp["mem0"].environment` (the mechanism confirmed against `@opencode-ai/plugin` v1.18.34).
- [x] 2.3 Add `integrations/opencode/README.md` documenting installation (`opencode plugin add`), the plugin options, and the environment fallbacks; update the root `README.md` installation section (uvx/pip one-liner) while keeping it agent-agnostic.

## 3. Verification

- [x] 3.1 Build the adapter (`tsc` in `integrations/opencode`); run `python3 -m pytest tests/ -q` and `openspec validate "package-server-and-opencode-adapter"`.
- [x] 3.2 End-to-end: install the server via `uvx --from . mem0-mcp-server` (or `pip install .`), launch it with the adapter's env mapping to the real HTTPS hub (`MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, `MEM0_TLS_VERIFY_HOSTNAME=false`, `MEM0_API_KEY`), and confirm add/search/list/get/delete succeed with no 401.

## Workflow follow-up

- Archive after review with `/opsx-archive`; verify the `opencode-adapter` spec lands at `openspec/specs/opencode-adapter/spec.md`.
- Depends on `pass-all-hub-options-via-env` (archive that one first so the environment variables exist).
- Consider a deprecation/redirect note in the old `opencode-mem0-mcp` repository.
