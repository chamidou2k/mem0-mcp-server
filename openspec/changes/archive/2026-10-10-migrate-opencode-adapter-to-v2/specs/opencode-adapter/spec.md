# opencode-adapter Delta

## ADDED Requirements

### Requirement: The adapter supports the OpenCode V1 and V2 plugin APIs

The adapter SHALL function as an OpenCode plugin under both V1 and V2. Its
default export SHALL act as a V2 plugin module that registers the `mem0` server
through the MCP editor when its setup runs, and SHALL also expose a V1 `server`
hook that registers the same server through the configuration hook.

#### Scenario: Registered under OpenCode V2
- **WHEN** OpenCode loads the adapter as a V2 plugin module
- **THEN** its setup registers a local stdio `mem0` server through the MCP
  editor, with the forwarded environment

#### Scenario: Registered under OpenCode V1
- **WHEN** OpenCode loads the adapter as a V1 plugin
- **THEN** its `server` hook registers a local stdio `mem0` server through the
  configuration hook, with the same forwarded environment

#### Scenario: Equivalent registration
- **WHEN** the server is registered through either API
- **THEN** the server name (`mem0`), command (`mem0-mcp-server`), and forwarded
  environment are the same
