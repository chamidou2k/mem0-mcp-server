# Tasks

## 1. Generalize agent-host registration

- [x] 1.1 Generalize the opencode-adapter registration so the mem0 server can register with a supported AI agent host (`opencode` or `pi`) while keeping OpenCode registration working as before; verify `opencode mcp list` shows `mem0` connected after `opencode plugin add`.

## 2. Add pi integration

- [x] 2.1 Create `integrations/pi/` with the pi installation/registration walkthrough (install from the repository specifier, register the mem0 server, set `serverCommand`); verify pi can launch the mem0 stdio MCP server via the configured `serverCommand`.

## 3. Documentation

- [x] 3.1 Update the README Quick Start installation section to document per-agent install steps for `opencode` and `pi`; verify each documented command runs as written.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result.
