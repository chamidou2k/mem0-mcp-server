# Tasks

## 1. Config: empty-as-unset and default removal

- [x] 1.1 In `mem0_mcp_server.py`, treat `None`, empty, and whitespace-only `mem0_host`/`mem0_host_https` as unset in `load_config()` (normalize only non-empty values), and remove the hardcoded `mem0_host` default from `DEFAULT_CONFIG`. Verify with `python -c` snippets: an explicit HTTP host still resolves; empty/absent HTTP + set HTTPS resolves HTTPS-only; both empty resolves neither.
- [x] 1.2 Update `tests/test_config.py` for the new default (a config with no `mem0_host` no longer yields the old hardcoded host) and add cases for empty-string and whitespace-only values treated as unset. Verify `python3 -m pytest tests/test_config.py -q` passes.

## 2. Client selection matrix

- [x] 2.1 Make `Mem0Client` endpoints optional: build the HTTP client only when an HTTP host is resolved and the HTTPS client only when an HTTPS host is resolved. Verify with a unit test constructing clients for HTTP-only, HTTPS-only, both, and neither.
- [x] 2.2 Extend `_select_client()` for the full matrix: neither → raise a clear "no endpoint configured" error; HTTPS-only → return the HTTPS client with no probe; HTTP-only → return the HTTP client with no probe; both → probe HTTP and prefer/fallback as today. Verify with tests asserting the selected client and probe behavior per case.
- [x] 2.3 Extend `tests/test_fallback.py` with HTTPS-only (no `/health` probe, HTTPS used) and neither-configured (operation raises naming the missing options), and confirm the existing HTTP-only/both/recovery/both-down cases still pass. Verify `python3 -m pytest tests/test_fallback.py -q` passes.

## 3. Template and documentation

- [x] 3.1 Ensure `config.template.json` shows both `mem0_host` and `mem0_host_https` as optional string entries (empty = disabled) so empty-as-unset is representable. Verify `python3 -m json.tool config.template.json` succeeds.
- [x] 3.2 Update `README.md`: document the four selection cases (HTTP-only, HTTPS-only, both, neither), state that empty/null means not configured, note `mem0_host` no longer has a built-in default, and that HTTPS-only requires `cert_path`. Verify the documented keys and cases match `config.template.json` and the spec.

## 4. Integration checks

- [x] 4.1 Smoke-test startup: run `python mem0_mcp_server.py --config <cfg> --transport stdio` (timeout-bounded) for HTTPS-only and neither-configured configs; confirm no traceback and that startup logs show the expected effective endpoints. Verify both runs behave as expected.
- [x] 4.2 Run the full suite (`python3 -m pytest tests/ -q`) and `openspec validate "add-endpoint-selection-robustness"`; both must pass before archive.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `hub-connection` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/hub-connection/spec.md`.
