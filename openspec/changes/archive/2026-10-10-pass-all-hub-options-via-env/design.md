# Design

## Context

See `proposal.md` - Why. The server already loads a JSON configuration file and then applies a fixed set of `MEM0_*` environment variables (see `load_config` in `mem0_mcp_server.py`). The three endpoint/TLS options were deliberately left out of that map. Endpoint resolution and `cert_path` validation already run after the environment pass, so they read whatever final value `config` holds.

## Goals / Non-Goals

**Goals:**
- Make every hub option settable through the environment, so an env-only MCP client can fully configure HTTP/HTTPS, the CA path, and hostname verification.
- Keep precedence and defaults identical to the existing `MEM0_HOST` behavior.

**Non-Goals:**
- Changing endpoint selection, TLS verification strength, or the JSON configuration-file schema.
- Accepting inline JSON on `--config` or otherwise changing config-file loading (the opencode adapter is fixed in the companion change).
- Adding new configuration *options*; only new environment *sources* for existing options.

## Decisions

- **Add the three names to the existing env map** rather than special-casing them: `MEM0_HOST_HTTPS` → `mem0_host_https`, `MEM0_CERT_PATH` → `cert_path`, `MEM0_TLS_VERIFY_HOSTNAME` → `tls_verify_hostname`. The current override loop already applies environment values before normalization/validation, so a single addition covers precedence and validation for free.
- **Parse `MEM0_TLS_VERIFY_HOSTNAME` through the existing `_parse_bool_option`**: the current code assigns the raw config value and then normalizes it with `_parse_bool_option(config.get(...), True)` after the env pass. Routing the env string through the same normalizer guarantees `true`/`false` (case-insensitive) semantics match the file boolean exactly.
- **Reuse existing validation** for `cert_path`: the HTTPS branch already requires a readable `cert_path` from `config`, regardless of source. No new validation path is needed.
- **Environment overrides the file.** Consistent with the existing `MEM0_HOST` mapping; an operator can override a checked-in file without editing it.

Alternatives considered:
- *Keep the options file-only and have clients write a temp config file*: rejected — duplicates secret material on disk and pushes file management onto every client.
- *Accept an inline JSON object on `--config`* (what the old opencode plugin attempted): rejected for the server — environment variables are the uniform, client-agnostic contract; the plugin bug is addressed in `package-server-and-opencode-adapter`.

## Risks / Trade-offs

- [Setting an env var to an empty string overrides and clears a file value] → Same behavior as the existing `MEM0_HOST` mapping; an empty endpoint value already means "not configured". Documented as consistent.
- [Making `tls_verify_hostname` env-settable relaxes a previously file-only safety control] → Chain verification against `cert_path` remains mandatory in all cases; only the hostname/IP match can be skipped. The risk is documented in the README; the requirement text keeps chain verification non-optional.
- [Silent precedence surprises] → Precedence matches the long-standing `MEM0_HOST` rule (env wins) and is stated in the spec scenarios.

## Migration Plan

Additive and backward compatible: existing config-file deployments are unaffected. No data or config migration. Rollback is reverting the code change.
