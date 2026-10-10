# Tasks

## 1. Add the root manifest

- [x] 1.1 Add `package.json` at the repository root with `name`, `version`, `private: true`, a short `description`, and `license: "MIT"`, and with no `scripts` or `workspaces`. Verify with `npm pkg get name version private` and confirm the Python suite still passes (`python3 -m pytest tests/ -q`).

## 2. Move the adapter's development dependencies to the root

- [x] 2.1 Add the adapter's build-time `devDependencies` (`@opencode-ai/plugin`, `@opencode/plugin`, `@types/node`, `typescript`) to the root `package.json`, and remove `devDependencies` from `integrations/opencode/package.json` (keeping `scripts`, `files`, and `peerDependencies`).
- [x] 2.2 Remove `integrations/opencode/package-lock.json` (the adapter ships no dependencies, and a lock would embed a mirror registry), and confirm `integrations/opencode/package.json` has no `devDependencies` (`npm pkg get devDependencies`).
- [x] 2.3 Verify the maintainer build still works: remove the adapter's `node_modules`, run `npm install` at the repository root, then build the adapter and confirm it compiles.

## 3. Verify the Git install

- [ ] 3.1 Commit and push the repository, then run `opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'` and confirm it succeeds and caches the adapter subdirectory (`node_modules/opencode-mem0-mcp` under the OpenCode npm cache).

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `opencode-adapter` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/opencode-adapter/spec.md`.
- Commit the root manifest and adapter package changes together with the archived change.
