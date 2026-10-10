# hub-connection Specification

## Purpose
Defines how the MCP server establishes its outbound connection to the remote mem0 hub: how the configured HTTP and HTTPS endpoints are selected, when the server falls back from HTTP to HTTPS, and what TLS verification the HTTPS endpoint requires.

## Requirements

### Requirement: HTTP endpoint is preferred for hub requests
The system SHALL treat a non-empty `mem0_host` as the configured HTTP endpoint and prefer it for hub requests. When both `mem0_host` and `mem0_host_https` are configured, the system SHALL check HTTP availability before each hub operation and send the operation to the HTTP endpoint when it responds; when only `mem0_host` is configured, the system SHALL send operations to it directly without probing.

#### Scenario: HTTP endpoint available
- **WHEN** both `mem0_host` and `mem0_host_https` are configured and the HTTP status check succeeds
- **THEN** the hub operation is sent to the HTTP endpoint and the HTTPS endpoint is not used

#### Scenario: HTTP only, no probing
- **WHEN** `mem0_host` is configured and `mem0_host_https` is empty or absent
- **THEN** operations are sent to the HTTP endpoint directly and no availability probe is performed

#### Scenario: Legacy config remains HTTP-only
- **WHEN** the configuration omits or leaves empty `mem0_host_https`
- **THEN** the server uses only the HTTP endpoint and performs no HTTPS fallback

### Requirement: HTTPS endpoint is used when HTTP is unavailable
When `mem0_host_https` is configured and the per-operation HTTP status check fails, the system SHALL send that operation to the HTTPS endpoint instead. The `mem0_host_https` value SHALL name the hub's HTTPS URL. Because HTTP is preferred, availability SHALL be re-checked on each operation so requests return to HTTP once it recovers.

#### Scenario: HTTP unavailable, HTTPS configured
- **WHEN** `mem0_host_https` is configured and the HTTP status check fails
- **THEN** the hub operation is sent to the HTTPS endpoint

#### Scenario: HTTP recovers
- **WHEN** a previous operation fell back to HTTPS and a later HTTP status check succeeds
- **THEN** the later operation is sent to the HTTP endpoint again

#### Scenario: Both endpoints unavailable
- **WHEN** `mem0_host_https` is configured and neither the HTTP status check nor the HTTPS operation succeeds
- **THEN** the operation fails with a connection error and the server keeps running (no startup failure)

### Requirement: HTTPS connections require a CA certificate location
When `mem0_host_https` is configured, the configuration (file or environment) SHALL also provide a `cert_path` option naming a CA certificate or bundle used to verify the hub's HTTPS certificate. Startup SHALL fail with a clear error if `cert_path` is missing from both sources or the file does not exist or cannot be read. Connections SHALL NOT fall back to unverified TLS.

#### Scenario: HTTPS endpoint configured without cert_path
- **WHEN** `mem0_host_https` is set and `cert_path` is absent from both the configuration file and the environment
- **THEN** the server fails at startup with an error stating that `cert_path` is required for the HTTPS endpoint

#### Scenario: cert_path points to a missing file
- **WHEN** `mem0_host_https` is set and the file at `cert_path` does not exist or is unreadable
- **THEN** the server fails at startup with an error naming the configured path

#### Scenario: Hub certificate verified against the configured CA
- **WHEN** `mem0_host_https` and a valid `cert_path` are configured and the hub presents a certificate signed by that CA
- **THEN** HTTPS requests succeed with TLS verification performed against the configured CA file

#### Scenario: Hub certificate cannot be verified
- **WHEN** the hub's HTTPS certificate is not signed by the CA at `cert_path`
- **THEN** the HTTPS request fails with a TLS verification error and no unverified connection is made

### Requirement: HTTPS endpoint is used when no HTTP endpoint is configured
When `mem0_host` is empty or absent and `mem0_host_https` is configured, the system SHALL send hub operations to the HTTPS endpoint directly, without probing an HTTP endpoint.

#### Scenario: HTTPS-only configuration
- **WHEN** `mem0_host` is empty or absent and `mem0_host_https` is configured
- **THEN** hub operations are sent to the HTTPS endpoint directly and no HTTP probe is performed

### Requirement: Operations fail clearly when no endpoint is configured
When neither `mem0_host` nor `mem0_host_https` is configured, the server SHALL still start, and each hub operation SHALL fail with a clear error stating that no mem0 endpoint is configured.

#### Scenario: Neither endpoint configured
- **WHEN** both `mem0_host` and `mem0_host_https` are empty or absent
- **THEN** the server starts successfully and each hub operation fails with an error stating that no endpoint is configured

### Requirement: HTTPS hostname verification is configurable
The system SHALL accept a `tls_verify_hostname` configuration option (boolean, default `true`). When `true`, the hub certificate SHALL be verified against `cert_path` including a hostname/IP match. When `false`, the chain SHALL still be verified against `cert_path` but the hostname/IP match SHALL be skipped. Chain verification SHALL remain mandatory in both cases; TLS verification SHALL NOT be disabled entirely.

#### Scenario: Default hostname verification
- **WHEN** `tls_verify_hostname` is absent or `true` and the hub certificate is valid for the connection hostname
- **THEN** the HTTPS request succeeds with full verification, including the hostname/IP match

#### Scenario: Hostname mismatch rejected by default
- **WHEN** `tls_verify_hostname` is `true` and the hub certificate is not valid for the connection hostname
- **THEN** the HTTPS request fails with a TLS verification error

#### Scenario: Opt-in hostname check skip
- **WHEN** `tls_verify_hostname` is `false` and the hub certificate is signed by the CA at `cert_path` but not valid for the connection hostname
- **THEN** the HTTPS request succeeds with the chain matched against `cert_path` and no hostname/IP check

#### Scenario: Chain still enforced when hostname check is skipped
- **WHEN** `tls_verify_hostname` is `false` and the hub certificate is not signed by the CA at `cert_path`
- **THEN** the HTTPS request fails with a TLS verification error and no unverified connection is made

### Requirement: Hub requests carry the configured API key
When an API key is configured (a non-empty `api_key` other than the literal `none`), the system SHALL send it as an `X-API-Key` request header on every request to the mem0 hub, for both the HTTP and HTTPS endpoints. When no API key is configured, the system SHALL NOT send an `X-API-Key` header.

#### Scenario: API key configured
- **WHEN** `api_key` is set to a non-empty value other than `none`
- **THEN** every hub request includes an `X-API-Key` header carrying that value

#### Scenario: API key not configured
- **WHEN** `api_key` is unset, empty, or the literal `none`
- **THEN** hub requests are sent without an `X-API-Key` header

#### Scenario: Auth-enforcing hub accepts the request
- **WHEN** the hub rejects `/memories` requests that lack an API key and a valid `api_key` is configured
- **THEN** storing and retrieving memories succeed instead of failing with an authorization error

### Requirement: Hub connection options can be set from environment variables
The system SHALL accept `mem0_host_https`, `cert_path`, and `tls_verify_hostname` from the environment variables `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, and `MEM0_TLS_VERIFY_HOSTNAME`, in addition to the JSON configuration file. Environment variables SHALL take precedence over the file. `MEM0_TLS_VERIFY_HOSTNAME` SHALL accept `true`/`false` (case-insensitive) with the same semantics as the configuration-file boolean.

#### Scenario: HTTPS endpoint from the environment
- **WHEN** `MEM0_HOST_HTTPS` and `MEM0_CERT_PATH` are set and the configuration file omits both `mem0_host_https` and `cert_path`
- **THEN** the server treats the HTTPS endpoint as configured and validates the certificate at the environment-provided `cert_path`

#### Scenario: Environment overrides the configuration file
- **WHEN** the configuration file sets `mem0_host_https` to one URL and `MEM0_HOST_HTTPS` sets another
- **THEN** the server uses the environment-variable URL

#### Scenario: Hostname-verification toggle from the environment
- **WHEN** `MEM0_TLS_VERIFY_HOSTNAME=false` is set
- **THEN** the hostname/IP match is skipped while the certificate chain is still verified against the configured CA

#### Scenario: Unset environment variables keep file and default behavior
- **WHEN** none of `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, or `MEM0_TLS_VERIFY_HOSTNAME` are set
- **THEN** these options come only from the configuration file or their defaults, with no behavior change

### Requirement: Server starts when a proxy is configured in the environment

When the process environment defines proxy variables, including a SOCKS proxy
such as `ALL_PROXY`, the server SHALL start successfully and SHALL NOT fail
during startup for lack of proxy support. Proxy selection SHALL follow the
standard environment variables, and hosts listed in `NO_PROXY` SHALL be
contacted directly. When no proxy variables are set, behavior SHALL be
unchanged.

#### Scenario: SOCKS proxy configured at startup

- **WHEN** the environment sets a SOCKS proxy (for example `ALL_PROXY=socks5://127.0.0.1:1080`) and a hub endpoint is configured
- **THEN** the server constructs its hub client and starts serving without raising a missing-proxy-support error

#### Scenario: No proxy configured

- **WHEN** no proxy environment variables are set
- **THEN** the server starts and reaches the hub exactly as before

#### Scenario: Hub host excluded from the proxy

- **WHEN** a proxy is configured and the hub host is listed in `NO_PROXY`
- **THEN** hub requests are sent directly, bypassing the proxy

#### Scenario: Client observes a live server

- **WHEN** the server is launched with proxy variables present
- **THEN** it keeps its standard input/output open and serves requests instead of exiting
