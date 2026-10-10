# server-version Specification

## Purpose

Lets clients, operators, and tests identify which build of the server is
running, so an upgrade can be confirmed rather than assumed.

## ADDED Requirements

### Requirement: The server reports its running version

The server SHALL expose its version as the MCP server metadata version and SHALL
include it in the `mem0_get_status` tool result.

#### Scenario: MCP server metadata carries the version
- **WHEN** an MCP client inspects the server's info
- **THEN** the reported server version is the server's version

#### Scenario: Status tool reports the version
- **WHEN** the `mem0_get_status` tool runs successfully
- **THEN** its result includes the server version

### Requirement: The command line can report the version

The server SHALL provide a `--version` option that prints the version and exits
without starting the server or requiring a hub connection.

#### Scenario: Printing the version
- **WHEN** the server is launched with `--version`
- **THEN** it prints the version and exits successfully

### Requirement: The reported version agrees with the installed package

The version reported through the MCP metadata, the status tool, and `--version`
SHALL be identical, and SHALL equal the installed `mem0-mcp-server` package
version when the package is installed.

#### Scenario: Reported and installed versions agree
- **WHEN** the server runs from an installed package
- **THEN** the version it reports equals the installed distribution's version

#### Scenario: All report surfaces agree
- **WHEN** the server reports its version through any surface
- **THEN** every surface reports the same value
