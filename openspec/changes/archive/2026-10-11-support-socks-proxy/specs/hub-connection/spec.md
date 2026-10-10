# Spec Delta

## ADDED Requirements

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
