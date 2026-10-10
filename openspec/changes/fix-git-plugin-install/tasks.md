# Tasks

## 1. Add the root manifest

- [x] 1.1 Add `package.json` at the repository root with `name`, `version`, `private: true`, a short `description`, and `license: "MIT"`, and with no `scripts` or `workspaces`. Verify with `npm pkg get name version private` and confirm the Python suite still passes (`python3 -m pytest tests/ -q`).

## 2. Verify the Git install

- [ ] 2.1 Commit and push the repository, then run `opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'` and confirm it succeeds and caches the adapter subdirectory (`node_modules/opencode-mem0-mcp` under the OpenCode npm cache).

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `opencode-adapter` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/opencode-adapter/spec.md`.
- Commit the root manifest together with the archived change.
