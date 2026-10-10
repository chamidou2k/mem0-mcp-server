# Design

## Context

`mem0_mcp_server.py` builds the HTTPS `httpx.AsyncClient` with `verify=cert_path`, which performs full verification including a hostname/IP match. The hub's certificate is self-signed (`CN=localhost`, no SAN), so connecting to `https://<hub>:8443` fails hostname verification even though the CA is trusted. Requirements live in `specs/hub-connection/spec.md` (delta in this change); motivation is in proposal.md. The current main spec forbids falling back to unverified TLS, so the relaxation must be explicit and keep chain verification.

## Goals / Non-Goals

**Goals:**
- Add an opt-in option to skip only the hostname/IP match while still verifying the chain against `cert_path`
- Default behavior unchanged (full verification)
- Keep `cert_path` mandatory for the HTTPS endpoint
- Config-file only, consistent with `mem0_host_https` and `cert_path`

**Non-Goals:**
- Disabling TLS verification entirely (`verify=False`) — never supported
- Certificate pinning by fingerprint, mTLS/client certificates
- Changing endpoint selection or fallback behavior
- Env-var support for the new option

## Decisions

**1. New option `tls_verify_hostname` (boolean, default `true`).**
Config-file only, matching the other HTTPS options (no `MEM0_*` mapping). Alternative: infer the relaxation from `cert_path` alone — rejected; the relaxation must be an explicit operator choice.

**2. `true` (default): keep `httpx.AsyncClient(..., verify=cert_path)` unchanged.**
No behavior change for existing configs and the current test suite remains valid.

**3. `false`: pass an `ssl.SSLContext` that still verifies the chain but skips the hostname match.**
Build the context with `ssl.create_default_context(cafile=cert_path)` (loads the platform defaults plus the configured CA), then set `check_hostname = False`. `verify_mode` stays `ssl.CERT_REQUIRED`. Alternative: `httpx.AsyncClient(verify=False)` — rejected; it disables all verification and violates the spec.

**4. Certificate verification stays mandatory; only the hostname/IP match is relaxed.**
`cert_path` is still required whenever `mem0_host_https` is set. A chain that does not match the configured CA still fails, and no unverified connection is made.

**5. Value parsing.**
Accept a JSON boolean; also accept the strings `"true"`/`"false"` case-insensitively for robustness. Any other value falls back to `true` (safe default).

**6. Endpoint selection unchanged.**
`tls_verify_hostname` only affects how the HTTPS client verifies; the HTTP-preferred/fallback logic is untouched.

## Risks / Trade-offs

- [Skipping the hostname check hides a cert/host mismatch (for example, a misdirected or impersonated endpoint)] → Opt-in and off by default; chain verification still limits trust to the configured CA.
- [`create_default_context` also trusts system CAs] → Acceptable; those roots are trusted by design. If single-CA pinning is later required, switch to a bare `ssl.SSLContext` with only `load_verify_locations(cert_path)`.
- [Operators set `false` broadly] → Documented as a security trade-off in the README; the safer alternative (fix the hub certificate to include a SAN for the hub address) is noted.
- [Existing `verify=cert_path` deprecation warning (httpx 0.28)] → Unchanged by this design; the `false` path uses an `SSLContext` and is not affected.

## Migration Plan

1. Deploy the code change; configs without `tls_verify_hostname` behave exactly as before (full verification).
2. Operators who need the relaxed check add `"tls_verify_hostname": false` (plus `mem0_host_https` and `cert_path`) and restart.
3. Rollback = remove the key or revert the code; no data or schema changes involved.

## Open Questions

None — the approach (trust the configured CA, skip only the hostname check) was chosen by the user before this design.
