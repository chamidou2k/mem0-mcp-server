# Tasks

## 1. Add SOCKS support to the runtime dependency

- [x] 1.1 In `pyproject.toml`, change the `httpx>=0.25.0` dependency to `httpx[socks]>=0.25.0`; verify with a throwaway venv (`python3 -m venv /tmp/ssx-venv && /tmp/ssx-venv/bin/pip install .`) that installation succeeds and `/tmp/ssx-venv/bin/python -c "import socksio"` imports without error.
- [x] 1.2 In `requirements.txt`, change `httpx>=0.25.0` to `httpx[socks]>=0.25.0`; verify a fresh venv `pip install -r requirements.txt` succeeds and `import socksio` works there too.

## 2. Document proxy behavior

- [x] 2.1 Add a README note explaining that the server honours standard proxy environment variables (including SOCKS) and that a LAN hub can be reached by listing its host in `NO_PROXY`; verify the note appears in `README.md` and the documented `NO_PROXY` variable name is spelled exactly.

## 3. Verify startup with a proxy configured

- [x] 3.1 With a hub endpoint configured, run the server with a SOCKS proxy in the environment (e.g. `ALL_PROXY=socks5://127.0.0.1:1080`) and confirm it starts and stays up instead of exiting with a missing-proxy-support error; capture the startup log line showing the configured HTTP host.
- [x] 3.2 Confirm the same launch with no proxy variables set still starts normally (no behavior change).
- [x] 3.3 Confirm `uv tool install --force --from . mem0-mcp-server` succeeds and the installed `mem0-mcp-server` binary starts under the SOCKS-proxy environment without the `ImportError`.
- [x] 3.4 Run the existing suite (`python3 -m pytest tests/ -q`) and confirm all tests still pass.

## Workflow follow-up

- Archive the change with `/opsx-archive` once review passes, and verify the `hub-connection` requirement landed in `openspec/specs/hub-connection/spec.md`.
- Commit the packaging, README, and change artifacts together with the archived change.
