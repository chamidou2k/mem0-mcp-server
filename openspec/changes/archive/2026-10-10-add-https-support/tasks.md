# Tasks

## 1. Config resolution and validation

- [x] 1.1 Add `mem0_host_https` and `cert_path` handling to `load_config()` in `mem0_mcp_server.py`: normalize the HTTP base URL from `mem0_host` (scheme-less → `http://`) and the optional HTTPS base URL from `mem0_host_https` (scheme-less → `https://`), expose both on the resolved config, and require `cert_path` when the HTTPS endpoint is present. Verify with `python -c` snippets loading temp config JSONs (legacy HTTP-only; both endpoints; HTTPS endpoint without `cert_path`).
- [x] 1.2 Add HTTPS validation in `load_config()`: when `mem0_host_https` is set, require `cert_path`, verify the file exists and is readable, and fail at startup with an error naming the path. Verify by loading temp configs with (a) no `cert_path`, (b) a nonexistent path — both must raise the documented messages.
- [x] 1.3 Add pytest unit tests for config behavior (legacy HTTP-only unchanged; both endpoints resolved with correct schemes; missing `cert_path`; missing/unreadable cert file; env vars do not set `mem0_host_https`/`cert_path`). Verify `python -m pytest tests/test_config.py -q` passes, and add `pytest` to a dev requirements file so the suite is reproducible.

## 2. HTTP-priority per-operation fallback

- [x] 2.1 Implement endpoint selection in `Mem0Client`: hold the HTTP client and an optional HTTPS client; before each hub operation, check availability via the HTTP status call and route the operation to HTTP when healthy, otherwise to the HTTPS endpoint. Verify with mock-transport unit tests asserting the routed base URL per operation.
- [x] 2.2 Add tests covering the fallback matrix: HTTP healthy → HTTP only; HTTP down + HTTPS configured → operation goes to HTTPS; HTTP recovers → a later operation returns to HTTP; HTTP down and no HTTPS endpoint → the connection error surfaces; both endpoints down → the operation fails and the server keeps running. Verify `python -m pytest tests/test_fallback.py -q` passes.

## 3. HTTPS client TLS wiring

- [x] 3.1 Construct the HTTPS client with `httpx.AsyncClient(base_url=<https>, verify=cert_path)` (no TLS kwargs on the HTTP client). Verify with a unit test asserting the HTTPS client's `base_url` scheme and that its transport was created with the configured CA path.
- [x] 3.2 Add an integration test using an `openssl`-generated self-signed CA and server cert against an in-process TLS endpoint: `verify=<ca>` succeeds, `verify=<wrong ca>` fails with a TLS verification error, and no unverified connection is made (skip cleanly if `openssl` is unavailable). Verify `python -m pytest tests/test_tls.py -q` passes.

## 4. Template and documentation

- [x] 4.1 Add `mem0_host_https` and `cert_path` keys to `config.template.json` with placeholder values. Verify `python -m json.tool config.template.json` succeeds and the keys appear.
- [x] 4.2 Update `README.md`: document the HTTP and HTTPS endpoints and `cert_path` in the configuration example and reference table, state that HTTP is preferred with per-operation HTTPS fallback and that HTTPS requires `cert_path`, and note these options are config-file only. Verify the table rows and example JSON match `config.template.json` keys.

## 5. Integration checks

- [x] 5.1 Smoke-test startup paths: run `python mem0_mcp_server.py --config <legacy-config>` (timeout-bounded) and confirm HTTP-only behavior; run with both endpoints configured and confirm startup logs show both base URLs with no traceback.
- [x] 5.2 Run the full test suite (`python -m pytest tests/ -q`) and `openspec validate "add-https-support"`; both must pass before archive.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `hub-connection` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/hub-connection/spec.md`.
