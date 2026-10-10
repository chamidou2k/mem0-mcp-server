# Design

## Context

- The adapter `integrations/opencode` is an npm package (`opencode-mem0-mcp`)
  built with `tsc`.
- It currently default-exports a V1 `PluginModule` (`{ id, server }`). The V1
  `server` hook returns a `config` hook that sets
  `config.mcp["mem0"] = { type: "local", command: ["mem0-mcp-server"],
  environment, enabled: true }`.
- OpenCode V2 (`opencode` 2.0.x) replaced the plugin API. V1 plugin
  implementations do not run in V2. V2 plugins use
  `Plugin.define({ id, setup })` from `@opencode/plugin`; options arrive on
  `ctx.options`; and MCP servers are registered through
  `ctx.mcp.transform((editor) => editor.set(name, config))`.
- The Python server and its `hub-connection` behavior are unaffected by this
  change.

## Decisions

### Dual-support default export

The package keeps a single default export that works on both V1 and V2, using
the documented dual-support pattern:

```ts
import { Plugin } from "@opencode/plugin";

export default {
  ...Plugin.define({
    id: "opencode-mem0-mcp",
    async setup(ctx) {
      await ctx.mcp.transform((editor) => {
        editor.set("mem0", {
          type: "local",
          command: ["mem0-mcp-server"],
          environment: buildEnvironment(ctx.options),
          disabled: false,
        });
      });
    },
  }),
  // V1 path: OpenCode V1 reads the module's `server` entrypoint.
  server(_input, options) {
    return {
      config: async (config) => {
        config.mcp ??= {};
        config.mcp["mem0"] = {
          type: "local",
          command: ["mem0-mcp-server"],
          environment: buildEnvironment(options),
          enabled: true,
        };
      },
    };
  },
};
```

Rationale: one published package serves both OpenCode generations; users on V2
get registration through the MCP editor, users on V1 keep the config hook. The
option→environment mapping (`OPTION_ENV_MAP`) and `buildEnvironment` helper are
reused unchanged so both paths forward the identical environment.

### V2 registration shape

V2 stores MCP servers under `mcp.servers`, so registration goes through
`ctx.mcp.transform` and the MCP editor rather than a raw `config.mcp` write. The
local server shape uses `disabled: false` (V2 field) instead of V1's
`enabled: true`.

### Dependencies

- Add `@opencode/plugin` (peer `>=2.0.0`, plus a dev dependency for types) for
  the V2 path.
- Keep `@opencode-ai/plugin` for the V1 `server` hook types.

## Risks / Tradeoffs

- `@opencode/plugin` carries heavier peer dependencies (SolidJS / OpenTUI). They
  are peers, not bundled, and the adapter itself imports only the `Plugin`
  factory and types. Verify the build types resolve.
- The exact MCP editor API and local-config field names are taken from the V2
  migration guide; confirm them while porting by building against the installed
  `@opencode/plugin` types. If a field differs, adjust to the real types.
- Dual export means the module is read by both loaders; keep the two paths in
  sync by sharing the mapping and helper code.

## Migration

Additive for consumers. V2 users gain a working plugin; V1 users are unchanged.
Rollback: revert the adapter files.

## Open Questions

- Does `ctx.mcp.transform`'s editor accept the same `environment` map? (Confirm
  against the installed types during implementation.)
