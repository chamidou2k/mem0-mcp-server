# opencode-adapter Specification

## ADDED Requirements

### Requirement: The adapter registers the mem0 MCP server

The adapter SHALL register a local stdio MCP server named `mem0` that runs the
installed `mem0-mcp-server` package.

#### Scenario: Registering the server
- **WHEN** the adapter's setup runs
- **THEN** it registers a stdio MCP server named `mem0` whose command launches
  the `mem0-mcp-server` entry point

### Requirement: The adapter forwards each supplied hub option as an environment variable

The adapter SHALL read its options from the OpenCode plugin configuration,
falling back to environment variables, and SHALL set each supplied option as the
corresponding `MEM0_*` environment variable for the server process. The adapter
SHALL NOT pass configuration as inline JSON on `--config`.

#### Scenario: Plugin options are forwarded using the documented mapping
- **WHEN** the plugin configuration supplies hub options
- **THEN** each option is set as the corresponding environment variable:

  | Plugin option | Environment variable |
  | --- | --- |
  | `mem0Host` | `MEM0_HOST` |
  | `mem0HostHttps` | `MEM0_HOST_HTTPS` |
  | `certPath` | `MEM0_CERT_PATH` |
  | `tlsVerifyHostname` | `MEM0_TLS_VERIFY_HOSTNAME` |
  | `apiKey` | `MEM0_API_KEY` |
  | `userId` | `MEM0_USER_ID` |
  | `agentId` | `MEM0_AGENT_ID` |
  | `channel` | `MEM0_CHANNEL` |
  | `searchThreshold` | `MEM0_SEARCH_THRESHOLD` |
  | `maxMemories` | `MEM0_MAX_MEMORIES` |
  | `infer` | `MEM0_INFER` |

#### Scenario: HTTPS and CA options are forwarded
- **WHEN** `mem0HostHttps`, `certPath`, and `tlsVerifyHostname` are supplied
- **THEN** the server receives `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, and
  `MEM0_TLS_VERIFY_HOSTNAME`

#### Scenario: Omitted options are left unset
- **WHEN** an option is not supplied by the plugin configuration or the
  environment
- **THEN** the adapter does not set that option, so the server's own default
  applies

#### Scenario: Environment fallback
- **WHEN** an option is missing from the plugin configuration but present as a
  `MEM0_*` environment variable
- **THEN** the adapter uses the environment value
