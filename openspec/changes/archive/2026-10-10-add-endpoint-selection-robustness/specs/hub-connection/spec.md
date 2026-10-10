# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
