# Proposal: Use generic example values in docs and server defaults

## Why

The repository is public, yet several committed files embed the maintainer's
private environment values:

- The hub's LAN address and ports (`192.168.1.100`, `:8001`, `:8443`) appear in
  user-facing examples in the root README and the adapter README.
- The server's default `user_id` is the maintainer's username (`"ssc"`).
- Archived OpenSpec artifacts reference the same LAN address, ports, and the
  maintainer's absolute local path (`/home/ssc/...`).

Anyone cloning the repo should not see another operator's private values; the
examples should be readable placeholders and the server should not ship with a
personal default identity.

## What Changes

- **Docs examples** (root `README.md`, `integrations/opencode/README.md`):
  replace `http://192.168.1.100:8001` with `http://<mem0-host>:8001`,
  `https://192.168.1.100:8443` with `https://<mem0-host>:8443`, and the
  placeholder key `change-me` with `<api-key>`.
- **Server default `user_id`** (`mem0_mcp_server.py`): change the fallback from
  `"ssc"` to the generic `"default"` in both `DEFAULT_CONFIG` and the
  `Mem0Client` constructor signature default. Operators who set `user_id`
  explicitly (file, env `MEM0_USER_ID`, or the adapter's `userId` option) are
  unaffected.
- **Archived OpenSpec artifacts**: scrub the private LAN address/ports/paths in
  the text of archived change documents; facts are preserved, only the concrete
  values become generic.
- **Maintainer's private config** (not committed): add an explicit
  `"userId": "ssc"` to the global plugin options so the maintainer's existing
  memories (stored under `user_id=ssc`) keep working after the default change.

## Capabilities

No capability is modified. The adapter option surface, hub-connection
endpoints, TLS, and API-key behavior are unchanged; only example text and a
private fallback default string change. `skip_specs` is declared because no
externally observable contract changes.

## Impact

- `README.md`, `integrations/opencode/README.md` — example values only.
- `mem0_mcp_server.py` — default `user_id` value only; no test asserts on the
  old value, so the suite stays green.
- Archived `openspec/changes/archive/*` documents — prose scrubbed.
- Behavior for existing deployments that set `user_id` explicitly: none.
  Deployments that relied on the bare default switch from namespace `ssc` to
  `default`.