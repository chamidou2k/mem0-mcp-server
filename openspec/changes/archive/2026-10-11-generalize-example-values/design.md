# Design: generalize example values

## Context

`grep -rn '192.168.1.100\|:8001\|:8443\|"ssc"'` shows the private values live
in three kinds of committed files:

1. User-facing docs: `integrations/opencode/README.md` (3 example blocks:
   Setup step 4, Configure example, V1-style plugin entry) and root `README.md`
   (TLS prose example + OpenCode options snippet).
2. Server defaults: `DEFAULT_CONFIG["user_id"] = "ssc"` and the
   `Mem0Client.__init__(user_id="ssc")` signature default.
3. Archived OpenSpec change artifacts (proposal/design/tasks prose).

Tests and `docker-compose.yml` already use generic names (`hub:8001`,
`mem0:8001`) and are untouched. `config.template.json` already uses `<user_id>`
placeholders.

## Decisions

### D1: Docs use `<mem0-host>` / `<api-key>` placeholders
Keep examples copyable: `mem0Host: "http://<mem0-host>:8001"`,
`mem0HostHttps: "https://<mem0-host>:8443"`, `apiKey: "<api-key>"`. The angle
brackets mark them as values to substitute. Chosen over real-looking fake IPs
(e.g. `10.0.0.1`) because a private-RFC address can still collide with an
operator's real LAN and mislead.

### D2: Server default `user_id` becomes `"default"`
Change both `DEFAULT_CONFIG` and the constructor default so the committed code
contains no personal identity. `"default"` rather than `""` because the mem0
hub API generally treats an empty `user_id` as missing/invalid; any string is a
valid memory namespace. `agent_id` stays `"opencode"` (a generic product name,
not a personal value).

### D3: Maintainer continuity via explicit private config
Memories are namespaced by `user_id` (+ `agent_id`). Changing the default would
otherwise strand the maintainer's existing data under `user_id=ssc`. Fix: add
`"userId": "ssc"` to the plugin options in the maintainer's private
`~/.config/opencode/opencode.json` (never committed), so behavior is identical
going forward. This is a local migration step, not a repo change.

### D4: Scrub archived artifact prose
Replace concrete values with generic text in archived OpenSpec documents (for
example `http://192.168.1.100:8001` → `http://<hub>:8001`, `192.168.1.100` →
the hub's address, `/home/ssc/projects/mem0-mcp-server` → the project path).
Facts and step descriptions stay intact; only identifiers are anonymized.

## Risks

- **Namespace fragmentation (D3)**: mitigated by pinning `userId: "ssc"` in
  the maintainer's config before/with the code default change.
- **`"default"` collision**: an operator who also happens to use the namespace
  "default" would share scope with bare-default deployments; acceptable, and
  documented as: always set `user_id` explicitly for isolation.
- **Docs drift**: placeholders are only helpful if examples stay consistent;
  grep-verified at merge time.

## Migration

Additive for the repo (default value + docs). Local rollout: update the private
plugin options with `"userId": "ssc"`, then deploy the new server version.
Rollback: restore the old default; memory namespaces are unaffected as long as
`userId` is pinned.