# Design

## Context

OpenCode installs a Git plugin by preparing the repository as a dependency and
then selecting the package named by `::path:`. The preparation step runs a
package install and, if the selected package declares lifecycle scripts, npm runs
them. The `mem0-mcp-server` repository is a Python project (`pyproject.toml` at
the root), and its adapter package declared `scripts` (`build`/`prepare`) that
invoke `tsc` - a tool the prepared checkout does not have. Preparation therefore
aborts with `git dep preparation failed` and the adapter is never installed.

Verified with throwaway directories and fresh OpenCode/npm caches each time
(`rm -rf ~/.cache/opencode ~/.npm/_cacache/tmp` before each attempt), varying
only `integrations/opencode/package.json`:

- Without a root `package.json`, the install fails (`ENOENT ... <clone>/package.json`).
- With a minimal private root `package.json`, `opencode plugin add
  'git+file://...#main::path:integrations/opencode'` succeeds and OpenCode caches
  the **subdirectory** package, proving it honors `::path:`.
- Adapter manifest exactly as shipped (`scripts: {build, prepublishOnly}`):
  **fails**.
- Adapter manifest with **no `scripts`**: **succeeds**.
- Adapter manifest with only `scripts: {prepublishOnly: "npm run build"}`:
  **succeeds**.
- Adapter manifest with only `scripts: {build: "tsc"}`: **fails**.
- Adapter manifest with only `scripts: {prepare: "tsc"}`: **fails**.
- Removing `peerDependencies` or `exports`, or trimming `files`, does **not**
  change the outcome (still fails, because the scripts are still present).

Conclusion: the discriminating factor is the presence of a build-bearing
lifecycle script (`build`/`prepare`) that npm runs during preparation.
`prepublishOnly` alone is harmless. The robust fix is for the adapter package to
declare no `scripts` at all, since `dist/` is committed and no build is ever
needed at install time.

Independently, system npm 9.2.0 ignores `::path:` (installs the root package) and
bun 1.4.2 rejects it, but OpenCode's bundled installer supports it. OpenCode is
the supported installer, so the fix targets it.

## Goals / Non-Goals

- Goal: the documented one-line Git install works.
- Non-Goal: publishing anything to npm; the root manifest is private.
- Non-Goal: changing the Python package or the adapter code.

## Decisions

### Decision: Add a minimal private root `package.json` that carries the dev dependencies

```json
{
  "name": "mem0-mcp-server",
  "version": "1.1.0",
  "private": true,
  "description": "mem0 MCP server and OpenCode adapter",
  "license": "MIT",
  "devDependencies": {
    "@opencode-ai/plugin": "^1.18.34",
    "@opencode/plugin": "^2.0.26",
    "@types/node": "^22.20.5",
    "typescript": "^5.6.0"
  }
}
```

- No `scripts` and no `workspaces`: the manifest exists to satisfy the
  installer's Git preparation step and to host the build-time dependencies for
  maintainers; it must not run side effects, so it stays script-free.
- `private: true` prevents accidental publication.
- `version` mirrors the Python server version (`mem0_mcp_server.__version__`)
  for human consistency; the file is never published, so drift is cosmetic.
- Alternative rejected: move the adapter to the repository root, which would
  break the server-plus-integrations layout and the Python packaging.
- Alternative rejected: a separate plugin repository, which duplicates the
  server and abandons the single-link install.
- Alternative rejected: keep the root manifest with no `devDependencies`, which
  leaves maintainers without a place to install TypeScript for the adapter build.

### Decision: The adapter package declares no `scripts` and no `devDependencies`

`integrations/opencode/package.json` keeps `files` and the optional
`peerDependencies`, but declares neither `scripts` nor `devDependencies`. Because
`dist/` is committed, the adapter needs nothing installed and nothing built at
install time, so OpenCode's Git preparation has no lifecycle to run and
succeeds. The build-time tooling (TypeScript, type packages) lives in the root
manifest instead; maintainers run `npm install` at the repository root, then
build with `npx tsc -p integrations/opencode`.

No npm lock files are committed. The adapter ships no dependencies, and a
generated lock embeds a machine-specific registry mirror plus the adapter's peer
tree, which is noise in a Python-first repository.

## Risks / Trade-offs

- A root `package.json` can make tooling treat the repository as a Node project.
  Mitigated by `private: true`, no scripts, and a stray root `node_modules/`
  already being git-ignored.
- Maintainers must `npm install` at the root (not in `integrations/opencode`) to
  get the build tooling; the adapter README documents the build command.
- The install still requires `uv` at runtime and an OpenCode that supports
  `::path:` (documented in the adapter README).

## Migration Plan

Additive. Rollback: delete the root `package.json` and restore the adapter's
`scripts`/`devDependencies`.

## Open Questions

None.
