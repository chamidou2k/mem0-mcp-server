# Tasks

## 1. Configuration option

- [x] 1.1 Add `tls_verify_hostname` (default `true`) to `DEFAULT_CONFIG` and handle it in `load_config()` in `mem0_mcp_server.py`: accept a JSON boolean and the strings `"true"`/`"false"` case-insensitively, defaulting to `true` for any other value; do not add an env-var mapping (config-file only). Verify with `python -c` snippets: absent → `True`; `false` and `"false"` → `False`; env var alone does not change it.
- [x] 1.2 Extend `tests/test_config.py` with cases for the new option (default `true`, explicit `false`, string `"false"`, and that `MEM0_TLS_VERIFY_HOSTNAME` does not set it). Verify `python3 -m pytest tests/test_config.py -q` passes.

## 2. HTTPS client TLS wiring

- [x] 2.1 In `Mem0Client`, when `tls_verify_hostname` is `false`, build the HTTPS client with `httpx.AsyncClient(..., verify=<ssl.SSLContext>)` where the context is `ssl.create_default_context(cafile=cert_path)` with `check_hostname = False` and `verify_mode` left at `ssl.CERT_REQUIRED`; when `true` (default), keep `verify=cert_path`. Verify with a unit test asserting the `false` path yields a context with `check_hostname` `False` and `verify_mode == ssl.CERT_REQUIRED`, and the `true` path is unchanged.
- [x] 2.2 Add an `openssl` integration test where the TLS endpoint presents a certificate valid only for a different name than the client connects to: default (`tls_verify_hostname` `true`) fails with a TLS verification error, and `false` succeeds. Skip cleanly if `openssl` is unavailable. Verify `python3 -m pytest tests/test_tls.py -q` passes.

## 3. Template and documentation

- [x] 3.1 Add `"tls_verify_hostname": true` to `config.template.json`. Verify `python3 -m json.tool config.template.json` succeeds and the key appears.
- [x] 3.2 Update `README.md`: document `tls_verify_hostname` in the config example and reference table (default `true`; set `false` to skip the hostname/IP match while the chain is still verified against `cert_path`; config-file only), and note the security trade-off plus the safer alternative of adding a SAN to the hub certificate. Verify the documented key and cases match `config.template.json` and the spec.

## 4. Integration checks

- [x] 4.1 Real-hub smoke test: HTTPS-only config targeting `https://192.168.1.100:8443` with `cert_path` pointing at the hub's self-signed certificate — confirm `get_status` fails with the default `tls_verify_hostname` and succeeds with `tls_verify_hostname: false`. Verify both runs behave as expected.
- [x] 4.2 Run the full suite (`python3 -m pytest tests/ -q`) and `openspec validate "add-tls-hostname-verify-option"`; both must pass before archive.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `hub-connection` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/hub-connection/spec.md`.
