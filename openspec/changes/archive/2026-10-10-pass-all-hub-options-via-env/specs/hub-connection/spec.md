# Spec Delta

## REMOVED Requirements

### Requirement: New endpoint options are configuration-file only
**Reason**: Clients such as the opencode adapter can only pass configuration to the server through environment variables, so restricting `mem0_host_https`, `cert_path`, and `tls_verify_hostname` to the configuration file made an HTTPS hub impossible to configure without shipping a file. Every hub option now has an environment equivalent.
**Migration**: Set `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, and `MEM0_TLS_VERIFY_HOSTNAME` instead of (or in addition to) the corresponding configuration-file keys. Environment variables override the file; all other behavior is unchanged.

## ADDED Requirements

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

## MODIFIED Requirements

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
