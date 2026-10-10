# Tasks

## 1. Launch the server from the repository

- [x] 1.1 Replace the bare `mem0-mcp-server` launch command with a default command array that runs the server through `uvx` from the project repository (`["uvx", "--from", "git+https://github.com/chamidou2k/mem0-mcp-server", "mem0-mcp-server"]`), used by both the V1 `server` hook and the V2 setup, and keep `npm run build` clean. Verify the registered command is the uvx array.
- [x] 1.2 Add an optional `serverCommand` option (a string or an array of strings, normalized to a command array) that overrides the default. Verify the option takes precedence over the default command.

## 2. Ship the compiled entry point

- [x] 2.1 Stop ignoring `integrations/opencode/dist` (change `.gitignore` `dist/` to `/dist/` so only the repository root is ignored) and track the built output. Verify a fresh checkout contains `dist/index.js` and `dist/index.d.ts`.

## 3. Documentation

- [x] 3.1 Update `integrations/opencode/README.md` with the one-line GitHub install (`opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'`), the `uv` prerequisite, and the `serverCommand` option; update the root README installation section to point at it.

## 4. Verification

- [x] 4.1 Build the adapter (`npm run build`), run the Node smoke test (asserting the default uvx command and the `serverCommand` override), run `python3 -m pytest tests/ -q`, and run `openspec validate "install-plugin-from-github"`.
- [x] 4.2 Install `uv` if absent and run the default command locally (`uvx --from /home/ssc/projects/mem0-mcp-server mem0-mcp-server --version`) to prove `uvx` launches the server; confirm it reports the version.

## Workflow follow-up

- After implementation review passes, archive the change with `/opsx-archive` so the `opencode-adapter` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/opencode-adapter/spec.md`.
- Commit the source, the tracked `dist/`, and the documentation together.
