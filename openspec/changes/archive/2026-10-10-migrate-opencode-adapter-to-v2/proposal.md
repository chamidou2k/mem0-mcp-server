# Proposal

## Why

The OpenCode adapter (`integrations/opencode`) targets the V1 plugin API
(`@opencode-ai/plugin`, default export `{ id, server }`, registration through a
`config` hook that writes `config.mcp["mem0"]`). OpenCode V2 changed the plugin
API, and V1 plugin implementations do not run in V2, so on a current OpenCode
the plugin loads but registers nothing. The adapter must speak the V2 API while
remaining usable on V1.

## What Changes

- Port `integrations/opencode/src/index.ts` to the V2 plugin API: default-export
  a module built with `Plugin.define({ id, setup })` that registers the `mem0`
  server through the MCP editor (`ctx.mcp.transform`) and reads options from
  `ctx.options`.
- Keep V1 compatibility in the same default export using the documented
  dual-support pattern (spread the V2 module and also provide a V1 `server()`
  hook). One package therefore works on both OpenCode V1 and V2.
- Add `@opencode/plugin` as a peer/dev dependency; keep `@opencode-ai/plugin`
  for the V1 path. The option→environment mapping and helper logic are
  unchanged.
- Update the adapter README to document V2 registration, options via
  `ctx.options`, and dual V1/V2 support.
- Not do: change the Python server or `hub-connection` behavior, publish to a
  registry, or install/register the plugin in any local OpenCode configuration.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `opencode-adapter`: the adapter additionally supports the OpenCode V2 plugin
  API (and continues to support V1), registering the same `mem0` server with the
  same forwarded environment through whichever API the running version loads.

## Impact

- `integrations/opencode/src/index.ts` (dual V1/V2 entrypoint)
- `integrations/opencode/package.json` (add `@opencode/plugin`, keep
  `@opencode-ai/plugin`)
- `integrations/opencode/README.md` (V2 documentation)
- No changes to `mem0_mcp_server.py`, `tests/`, or the global OpenCode config.
