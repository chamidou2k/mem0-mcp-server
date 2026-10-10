# Tasks

## 1. Make the compiled adapter self-contained

- [x] 1.1 In `integrations/opencode/src/index.ts`, remove the runtime `import { Plugin } from "@opencode/plugin"` and define the V2 plugin as a plain `{ id, setup }` object (equivalently, inline the identity `Plugin.define`). Declare the used OpenCode surface (`PluginOptions`, the MCP editor, the setup context, and the plugin module) with local structural types.
- [x] 1.2 Rebuild `dist/` with `npx tsc -p integrations/opencode` and confirm the compiled `dist/index.js` contains no `import`/`require` of any package.
- [x] 1.3 Verify the compiled module loads in isolation: copy `dist/index.js` to a directory with no `node_modules` and import it, confirming the default export exposes `id`, `setup`, and `server`.

## 2. Drop the unused package relationships

- [x] 2.1 Remove `peerDependencies` and `peerDependenciesMeta` from `integrations/opencode/package.json`.
- [x] 2.2 Remove `@opencode-ai/plugin` and `@opencode/plugin` from the root `package.json` `devDependencies` (keep `typescript` and `@types/node`).
- [x] 2.3 Update `integrations/opencode/README.md` to describe the plain V2 module rather than `Plugin.define`.

## 3. Verify the end-to-end Git install

- [x] 3.1 Commit and push, then reinstall from `github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode` with OpenCode and npm caches cleared, and confirm OpenCode's log shows the plugin loading (no `Cannot find package` warning) and `mem0` connected.
- [x] 3.2 Remove the local wrapper `~/.config/opencode/plugins/opencode-mem0-mcp.js` so `mem0` is served only by the Git-installed plugin, restart the service, and confirm `mem0` remains connected.
- [x] 3.3 Document the `uvx` cold-start/concurrency caveat and the `uv tool install` + `serverCommand` remedy in `integrations/opencode/README.md`.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `opencode-adapter` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/opencode-adapter/spec.md`.
- Commit the adapter, manifest, README, and `dist/` changes together with the archived change.
