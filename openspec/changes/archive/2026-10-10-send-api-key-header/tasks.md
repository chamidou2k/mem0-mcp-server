# Tasks

## 1. API-key header wiring

- [x] 1.1 In `Mem0Client.__init__`, add an `X-API-Key` header to the shared `headers` dict when `api_key` is non-empty and not the literal `none` (so both the HTTP and HTTPS clients inherit it), leaving the other headers unchanged. Verify with a unit test asserting `X-API-Key` is present with the configured value when a key is set.
- [x] 1.2 Extend `tests/test_client.py` with the header matrix: a configured key → `X-API-Key` present on both the HTTP and HTTPS clients; empty and `none` → header absent. Verify `python3 -m pytest tests/test_client.py -q` passes.

## 2. Documentation

- [x] 2.1 Update `README.md`: document that a configured `api_key` is sent as an `X-API-Key` header, that `none`/empty sends no header, and recommend HTTPS when a key is used. Verify the README statements match the code behavior and the `hub-connection` spec.

## 3. Integration checks

- [x] 3.1 Real-hub smoke test: HTTPS config to `https://192.168.1.100:8443` with `cert_path` and a real `api_key` — confirm add/search/list/get/delete all succeed (no 401). Verify the observed behavior.
- [x] 3.2 Run the full suite (`python3 -m pytest tests/ -q`) and `openspec validate "send-api-key-header"`; both must pass.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `hub-connection` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/hub-connection/spec.md`.
- Note: the completed changes `add-endpoint-selection-robustness` and `add-tls-hostname-verify-option` also still await archiving.
