# Tasks

## 1. Add the root manifest

- [x] 1.1 Add `package.json` at the repository root with `name`, `version`, `private: true`, a short `description`, and `license: "MIT"`, and with no `scripts` or `workspaces`. Verify with `npm pkg get name version private` and confirm the Python suite still passes (`python3 -m pytest tests/ -q`).

## 2. Move the adapter's development dependencies to the root

- [x] 2.1 Add the adapter's build-time `devDependencies` (`@opencode-ai/plugin`, `@opencode/plugin`, `@types/node`, `typescript`) to the root `package.json`.
- [x] 2.2 Remove `integrations/opencode/package-lock.json` (the adapter ships no dependencies, and a lock would embed a mirror registry), and confirm `integrations/opencode/package.json` declares no `devDependencies` (`npm pkg get devDependencies`).

## 3. Remove the adapter's lifecycle scripts

- [x] 3.1 Remove the `scripts` block (`build`, `prepublishOnly`) from `integrations/opencode/package.json`. Rationale: OpenCode's Git preparation runs the selected package's lifecycle scripts, and `tsc` is absent in the prepared checkout, so the install failed with `git dep preparation failed`. Confirmed by bisection: adapter with no `scripts` installs; adapter with `build`/`prepare` fails.
- [x] 3.2 Update the adapter README's Development section to build from the repository root (`npm install` then `npx tsc -p integrations/opencode`), since the adapter package no longer has a `build` script.
- [x] 3.3 Verify the maintainer build still works: from the repository root run `npm install` and `npx tsc -p integrations/opencode`, and confirm it compiles and `dist/` is unchanged.

## 4. Verify the Git install

- [x] 4.1 Commit and push the repository, then run `opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'` (with OpenCode and npm caches cleared) and confirm it succeeds and caches the adapter subdirectory (`node_modules/opencode-mem0-mcp` under the OpenCode npm cache).

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `opencode-adapter` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/opencode-adapter/spec.md`.
- Commit the root manifest and adapter package changes together with the archived change.
