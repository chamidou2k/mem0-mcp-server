# Tasks

## 1. Plugin README setup walkthrough

- [x] 1.1 Add a step-by-step **Setup** section to `integrations/opencode/README.md` that takes a new machine to `mem0 connected`: install `uv`, (recommended) `uv tool install` the server, `opencode plugin add '...'`, convert the entry to the object form with hub options in `opencode.json`, `opencode service restart`, and verify with `opencode mcp list`; verify each of those commands/keys appears in the section (`grep -n 'opencode plugin add\|opencode service restart\|opencode mcp list\|"options"' integrations/opencode/README.md`).
- [x] 1.2 Link the setup steps to the existing `## Startup latency` section and the server README's proxy note, so the fast-start remedy and the `NO_PROXY` caveat are reachable in context; verify the referenced section/heading names actually exist.

## 2. Root README cross-reference

- [x] 2.1 Expand the "Client Integrations -> OpenCode" section of the root `README.md` with the concise install+configure+verify flow and a link to the adapter README for details; verify the section shows `opencode plugin add`, the object-form option snippet, and `opencode mcp list`.

## Workflow follow-up

- Archive the change after review and verify the docs render as intended.
- Commit the README edits together with the archived change.
