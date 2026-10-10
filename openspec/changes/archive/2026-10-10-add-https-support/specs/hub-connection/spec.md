# Spec Delta

## Purpose

Defines how the MCP server establishes its outbound connection to the remote mem0 hub: how the configured HTTP and HTTPS endpoints are selected, when the server falls back from HTTP to HTTPS, and what TLS verification the HTTPS endpoint requires.

## ADDED Requirements

### Requirement: HTTP endpoint is preferred for hub requests
The system SHALL treat `mem0_host` as the HTTP endpoint and prefer it for hub requests. Before each hub operation the system SHALL check HTTP availability via the hub status call; when HTTP responds, the operation SHALL be sent to the HTTP endpoint.

#### Scenario: HTTP endpoint available
- **WHEN** `mem0_host` is configured and the HTTP status check succeeds
- **THEN** the hub operation is sent to the HTTP endpoint and the HTTPS endpoint is not used

#### Scenario: Legacy config remains HTTP-only
- **WHEN** the configuration omits `mem0_host_https`
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
When `mem0_host_https` is configured, the configuration SHALL also provide a `cert_path` option naming a CA certificate or bundle used to verify the hub's HTTPS certificate. Startup SHALL fail with a clear error if `cert_path` is missing or the file does not exist or cannot be read. Connections SHALL NOT fall back to unverified TLS.

#### Scenario: HTTPS endpoint configured without cert_path
- **WHEN** `mem0_host_https` is set and `cert_path` is absent from the configuration file
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

### Requirement: New endpoint options are configuration-file only
The `mem0_host_https` and `cert_path` options SHALL be read only from the JSON configuration file. Environment variables SHALL NOT set these options.

#### Scenario: Env var does not set the HTTPS endpoint
- **WHEN** only the environment variable `MEM0_HOST_HTTPS` is set and the config file omits `mem0_host_https`
- **THEN** `mem0_host_https` remains unset and the server operates HTTP-only
