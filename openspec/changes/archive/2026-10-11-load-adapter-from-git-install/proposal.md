# Proposal

## Why

The one-line Git install now succeeds, but the installed plugin does not load.
OpenCode's log records:

```
failed to load plugin target=github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode
cause="Cannot find package '@opencode/plugin' imported from
  .../node_modules/opencode-mem0-mcp/dist/index.js"
```

The compiled adapter keeps a runtime `import { Plugin } from "@opencode/plugin"`
and calls `Plugin.define(...)`. A Git-installed plugin lives in OpenCode's npm
cache, where OpenCode's own packages (`@opencode/plugin`) are **not** resolvable,
so the import throws and the plugin never registers the `mem0` server. The
"installs from the project repository" requirement is satisfied for installation
but not for loading, so the feature is still unusable end to end.

## What Changes

- Stop importing `@opencode/plugin` at runtime. `Plugin.define` is the identity
  function, so the V2 plugin is defined directly as a plain
  `{ id, setup }` object.
- Declare the small OpenCode V2 surface the adapter uses (options, MCP editor,
  setup context, plugin module) with local structural types instead of importing
  them, so the compiled entry point imports nothing at runtime.
- Rebuild `dist/` so the committed entry point is self-contained.
- Remove the now-unused `peerDependencies` from the adapter package and the
  OpenCode build-time packages from the root manifest.
- Update the adapter README to describe the plain V2 module.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `opencode-adapter`: the "installs from the project repository" requirement now
  also requires the compiled entry point to have no runtime package dependencies
  so it loads from the installer's cache.

## Impact

- `integrations/opencode/src/index.ts` and the rebuilt
  `integrations/opencode/dist/`.
- `integrations/opencode/package.json` (drop `peerDependencies`) and the root
  `package.json` (drop the OpenCode build-time devDependencies).
- `integrations/opencode/README.md`.
- The Python server is unchanged.
