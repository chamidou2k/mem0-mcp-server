# opencode-adapter Specification

## Purpose
Registers the mem0 MCP server with OpenCode through a plugin: the plugin launches the server on demand and forwards hub connection options to it as environment variables, so users get persistent memory without editing server configuration files.

## Requirements

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

### Requirement: The adapter installs from the project repository

The adapter SHALL be installable from the project's Git repository with a single
specifier and without a build step. The repository SHALL contain a root
`package.json`, marked `private`, so the installer's Git dependency preparation
step succeeds. The adapter package SHALL NOT declare `devDependencies` and SHALL
NOT declare `scripts`, so preparation resolves no adapter dependencies and runs
no lifecycle build. The compiled entry point referenced by the adapter package's
`main`/`exports` fields SHALL be committed to the repository.

#### Scenario: Git install needs no build
- **WHEN** the adapter package is resolved from the Git repository
- **THEN** the compiled entry point (`dist/index.js`) referenced by
  `main`/`exports` is present in the checkout

#### Scenario: Repository root resolves for a Git install
- **WHEN** the installer prepares the repository as a Git dependency
- **THEN** it finds a root `package.json` and can then select the adapter package
  from `integrations/opencode`

#### Scenario: Preparation runs no adapter lifecycle
- **WHEN** the installer prepares the adapter package as a Git dependency
- **THEN** the adapter package declares no `devDependencies` and no `scripts`, so
  preparation neither installs adapter dependencies nor runs a build script, and
  the preparation succeeds
