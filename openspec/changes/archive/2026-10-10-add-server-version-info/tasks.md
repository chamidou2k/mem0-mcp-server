# Tasks

## 1. Single source of truth

- [x] 1.1 Add `__version__ = "1.1.0"` as a top-level literal in `mem0_mcp_server.py` and use it in `MCPServer(name="mem0-mcp", version=__version__)`. Verify with a test asserting the version used by `create_mcp_server` equals `mem0_mcp_server.__version__`.
- [x] 1.2 Make `pyproject.toml` derive its version from the module (`dynamic = ["version"]` plus `[tool.setuptools.dynamic] version = { attr = "mem0_mcp_server.__version__" }`). Verify a build/install reports package metadata version `1.1.0`.

## 2. Report surfaces

- [x] 2.1 Add a `--version` option to the CLI (`argparse` version action using `__version__`). Verify `mem0-mcp-server --version` prints the version and exits `0` without loading config or contacting the hub.
- [x] 2.2 Include `server_version` in the `mem0_get_status` tool's JSON result (both success and error payloads). Verify with a test that the success payload contains the server version.

## 3. Documentation

- [x] 3.1 Document how to check the running server version in `README.md` (the status tool and the `--version` option). Verify the documented commands match the implemented behavior.

## 4. Integration checks

- [x] 4.1 Run the full suite (`python3 -m pytest tests/ -q`) and `openspec validate "add-server-version-info"`; both must pass.
- [x] 4.2 Reinstall the package (`python3 -m pip install --user --break-system-packages .`), confirm `mem0-mcp-server --version` reports `1.1.0`, and confirm a real-hub `mem0_get_status` returns `server_version` `1.1.0` while add/search/list/get/delete still succeed (no 401).

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `server-version` capability merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/server-version/spec.md`.
- Commit the resulting changes.
