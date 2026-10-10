# Proposal

## Why

Clients such as the opencode adapter can only pass configuration to the server through environment variables, but the HTTPS endpoint, CA certificate path, and hostname-verification toggle are currently configuration-file only. As a result an env-only client cannot configure an HTTPS hub at all and must fall back to shipping a config file. Giving every hub option an environment-variable mapping establishes one uniform contract that all MCP clients can use.

## What Changes

- Extend the environment-variable mapping in `load_config` with the three remaining hub options:
  - `MEM0_HOST_HTTPS` → `mem0_host_https`
  - `MEM0_CERT_PATH` → `cert_path`
  - `MEM0_TLS_VERIFY_HOSTNAME` → `tls_verify_hostname`
- `MEM0_TLS_VERIFY_HOSTNAME` accepts `true`/`false` (case-insensitive), with the same semantics as the config-file boolean (default `true`).
- Environment variables continue to override the configuration file; defaults are unchanged.
- **BREAKING** (stated requirement reversal): the `hub-connection` requirement "New endpoint options are configuration-file only" is removed and replaced by a requirement allowing every hub option to come from environment variables.
- The HTTPS CA-certificate requirement now treats `cert_path` as missing only when neither the configuration file nor the environment supplies it, and reports startup errors accordingly.

## Capabilities

### New Capabilities
<!-- None: no new capability is introduced; an existing requirement is relaxed. -->

### Modified Capabilities
- `hub-connection`: allow `mem0_host_https`, `cert_path`, and `tls_verify_hostname` to be supplied through environment variables; remove the configuration-file-only restriction and adjust the CA-certificate requirement's wording so a missing `cert_path` means missing from both sources.

## Impact

- `mem0_mcp_server.py` — `load_config` environment mapping and the HTTPS/cert validation path.
- `tests/test_config.py` — add cases covering the three new environment variables and precedence over the config file.
- No change to the hub protocol, endpoints, or the JSON configuration-file schema; the new names extend the existing `MEM0_*` environment set.
- Unblocks the `package-server-and-opencode-adapter` change, whose opencode adapter passes all options through the environment.
