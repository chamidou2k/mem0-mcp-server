# Spec Delta

## ADDED Requirements

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
