# Proposal

## Why

Internal/self-signed hub certificates — for example `CN=localhost` with no SAN — are rejected by hostname/IP verification even when the operator explicitly trusts the CA. As a result the HTTPS fallback endpoint cannot be used against the hub's configured address (`192.168.1.100`), even though the certificate is otherwise trusted. Operators need an explicit, opt-in way to keep certificate-chain verification while skipping only the hostname match.

## What Changes

- Add a `tls_verify_hostname` boolean config option (default `true`).
- When `true` (default): unchanged behavior — the hub certificate is verified against `cert_path` including a hostname/IP match.
- When `false`: the certificate chain is still verified against `cert_path`, but the hostname/IP match is skipped (an `ssl.SSLContext` with `check_hostname=False` and `verify_mode=CERT_REQUIRED`, trusting the configured CA).
- `cert_path` remains required whenever `mem0_host_https` is configured; TLS verification is never disabled entirely (`verify=False` is not supported).
- Config-file only (no environment-variable mapping), consistent with the other HTTPS options.
- Extend `config.template.json` and README configuration documentation.
- No change to endpoint selection, MCP tools, resources, transports, or the mem0 REST API surface.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hub-connection`: HTTPS certificate verification gains an explicit, opt-in hostname-check toggle while chain verification against `cert_path` remains mandatory.

## Impact

- `mem0_mcp_server.py`: `DEFAULT_CONFIG`, `load_config()`, and the HTTPS `httpx.AsyncClient` construction in `Mem0Client`
- `config.template.json`: new `tls_verify_hostname` key
- `README.md`: configuration reference table and example
- Dependencies: none added (uses the standard-library `ssl` module)
- Security: opt-in and off by default; only the hostname/IP match is relaxed, chain verification against `cert_path` is preserved, and unverified TLS is never allowed
