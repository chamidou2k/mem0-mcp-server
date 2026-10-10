# Tasks

## 1. Port the adapter entrypoint

- [x] 1.1 In `integrations/opencode/src/index.ts`, replace the V1-only default export with a dual-support export: spread `Plugin.define({ id: "opencode-mem0-mcp", setup })` from `@opencode/plugin` (V2, registering the `mem0` server through `ctx.mcp.transform` with options from `ctx.options`) and also provide the V1 `server` hook (registering through the `config` hook). Reuse `OPTION_ENV_MAP` and `buildEnvironment` so both paths forward the same environment. Verify `npm run build` (tsc) passes with no type errors.
- [x] 1.2 Update `integrations/opencode/package.json`: add `@opencode/plugin` (`>=2.0.0`) to `peerDependencies` (and a dev dependency for types), keep `@opencode-ai/plugin`. Verify `npm install` and `npm run build` succeed.

## 2. Documentation

- [x] 2.1 Update `integrations/opencode/README.md` to document V2: registration through the MCP editor (`ctx.mcp.transform`, `mcp.servers`), options read from `ctx.options`, the V2 `plugins` array (and the V1 `plugin` array), and that the adapter supports both V1 and V2. Verify the statements match the code.

## 3. Verification

- [x] 3.1 `npm run build` in `integrations/opencode` succeeds, and a Node smoke import of `dist/index.js` confirms the default export exposes both a V2 `setup` and a V1 `server` hook.
- [x] 3.2 Run `python3 -m pytest tests/ -q` (server unaffected) and `openspec validate "migrate-opencode-adapter-to-v2"`; both must pass.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `opencode-adapter` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/opencode-adapter/spec.md`.
- Installing/registering the plugin in a local OpenCode configuration is intentionally out of scope for this change.
