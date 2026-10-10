# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: New endpoint options are configuration-file only
The `mem0_host_https`, `cert_path`, and `tls_verify_hostname` options SHALL be read only from the JSON configuration file. Environment variables SHALL NOT set these options.

#### Scenario: Env var does not set the HTTPS endpoint
- **WHEN** only the environment variable `MEM0_HOST_HTTPS` is set and the config file omits `mem0_host_https`
- **THEN** `mem0_host_https` remains unset and the server operates HTTP-only

#### Scenario: Env var does not set the hostname-verification option
- **WHEN** only the environment variable `MEM0_TLS_VERIFY_HOSTNAME` is set and the config file omits `tls_verify_hostname`
- **THEN** `tls_verify_hostname` keeps its default behavior with hostname verification enabled
