# Design

## Context

OpenCode loads a plugin by importing its entry point from the location the
installer prepared. For a Git plugin that location is OpenCode's npm cache
(`~/.cache/opencode/npm/git-*/.../node_modules/opencode-mem0-mcp`). Only the
packages the installer resolved for that dependency are present there; OpenCode's
own runtime packages are not on the module-resolution path. The adapter's
compiled entry point imported `@opencode/plugin` at runtime, so the import
failed:

```
Cannot find package '@opencode/plugin' imported from
  .../node_modules/opencode-mem0-mcp/dist/index.js
```

Inspection of `@opencode/plugin@2.0.26` shows the only value the adapter used,
`Plugin.define`, is the identity function:

```js
// node_modules/@opencode/plugin/dist/promise/plugin.js
export function define(plugin) { return plugin; }
```

and `PluginOptions` is `Readonly<Record<string, any>>`. Neither requires a runtime
import: the type is erased by the compiler, and `define` adds nothing.

## Goals / Non-Goals

- Goal: the Git-installed adapter loads and registers `mem0`.
- Goal: the committed entry point is self-contained (no runtime imports).
- Non-Goal: publishing to npm.
- Non-Goal: changing the server launch command, options mapping, or V1 support.

## Decisions

### Decision: Define the V2 plugin as a plain object instead of `Plugin.define`

`Plugin.define` is the identity function, so
`Plugin.define({ id, setup })` is exactly `{ id, setup }`. Defining the object
directly removes the only runtime import. The default export remains
`{ ...v2Plugin, server }`, so the V1 `server` hook is unaffected.

### Decision: Declare the used OpenCode surface with local structural types

The adapter uses a very small API surface: `context.options`, and
`context.mcp.transform(editor => editor.set(name, server))`. Declaring minimal
local interfaces for these keeps the compile-time contract while importing
nothing, so the compiled module is self-contained. The trade-off is that
OpenCode API drift is not caught by the compiler; the surface is tiny and the
end-to-end Git-install test covers it.

### Decision: Drop the now-unused package relationships

With no runtime import and local types, the adapter needs neither
`peerDependencies` nor OpenCode build-time packages. Removing the adapter's
`peerDependencies`/`peerDependenciesMeta` and the root manifest's
`@opencode-ai/plugin` and `@opencode/plugin` devDependencies leaves the adapter
with no dependency graph, which is exactly why a Git install can load it.

## Risks / Trade-offs

- Local types could drift from the real OpenCode V2 API. Mitigated by verifying
  the plugin loads and registers `mem0` through a real Git install.
- A plain object relies on OpenCode reading `id`/`setup` off the default export
  rather than a branded `define` result; verified against `@opencode/plugin`
  source and the runtime load test.

## Migration Plan

Additive and backward compatible: the default export shape
(`{ id, setup, server }`) is unchanged, only its construction is. Rollback:
restore the `Plugin.define` call and re-add the dependencies.

## Open Questions

None.
