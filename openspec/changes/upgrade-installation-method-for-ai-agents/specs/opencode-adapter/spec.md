# Spec Delta

## MODIFIED Requirements

### Requirement: The adapter registers the mem0 MCP server
The adapter SHALL register a local stdio MCP server named `mem0` with a supported AI agent host (`opencode` or `pi`). By default it SHALL launch the server with `uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`, so installing the adapter also supplies the server. A `serverCommand` option SHALL override the default launch command. The agent host to register with is determined by the installation/registration procedure for that host.

#### Scenario: Registration with OpenCode
- **WHEN** the adapter is installed with OpenCode from the repository specifier
- **THEN** the `mem0` stdio MCP server is registered with OpenCode and launches via the configured `serverCommand` (default `uvx` from the repository)

#### Scenario: Registration with pi
- **WHEN** the adapter is installed and registered with pi from the repository specifier
- **THEN** the `mem0` stdio MCP server is available to pi and launches via the configured `serverCommand` (default `uvx` from the repository)
