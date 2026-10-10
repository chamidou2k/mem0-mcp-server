# Spec Delta

## MODIFIED Requirements

### Requirement: The adapter registers the mem0 MCP server

The adapter SHALL register a local stdio MCP server named `mem0`. By default it
SHALL launch the server with `uvx` from the project repository
(`uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`),
so installing the plugin also supplies the server. A `serverCommand` option
SHALL override the default launch command.

#### Scenario: Registering the server
- **WHEN** the adapter's setup runs
- **THEN** it registers a stdio MCP server named `mem0` whose command launches
  the `mem0-mcp-server` entry point from the project repository through `uvx`

#### Scenario: Overriding the launch command
- **WHEN** the plugin configuration supplies a `serverCommand`
- **THEN** the registered server uses that command instead of the default

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
- **THEN** the server name (`mem0`), the launch command, and the forwarded
  environment are the same

## ADDED Requirements

### Requirement: The adapter installs from the project repository

The adapter SHALL be installable from the project's Git repository with a single
specifier and without a build step: the compiled entry point referenced by the
package's `main`/`exports` fields SHALL be committed to the repository.

#### Scenario: Git install needs no build
- **WHEN** the adapter package is resolved from the Git repository
- **THEN** the compiled entry point (`dist/index.js`) referenced by
  `main`/`exports` is present in the checkout
