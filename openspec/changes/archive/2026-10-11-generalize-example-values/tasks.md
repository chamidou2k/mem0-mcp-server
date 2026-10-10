# Tasks

## Docs examples

- [x] 1.1 Replace private example values in `integrations/opencode/README.md`
      (Setup step 4, Configure example, V1-style entry):
      `http://192.168.1.100:8001` → `http://<mem0-host>:8001`,
      `https://192.168.1.100:8443` → `https://<mem0-host>:8443`,
      `change-me` → `<api-key>`.
- [x] 1.2 Replace the same in root `README.md`: the TLS prose example
      (`192.168.1.100`) → "the hub's address", and the OpenCode options
      snippet (`mem0Host`, `apiKey`).

## Server default

- [x] 2.1 Change `mem0_mcp_server.py`: `DEFAULT_CONFIG["user_id"]` and the
      `Mem0Client.__init__` default from `"ssc"` to `"default"`.
- [x] 2.2 Verify: `python3 -m pytest tests/ -q` stays green (56 passing); grep
      confirms no `192.168.1.100`, `:8001`/`:8443`, `change-me`, or `"ssc"`
      remain in committed non-archive files.

## Archive cleanup

- [x] 2.3 Scrub private values from archived OpenSpec artifact prose
      (`openspec/changes/archive/2026-10-10-*`): hub LAN address/ports and the
      `/home/ssc/...` path → generic text; keep facts intact.

## Maintainer migration (private, not committed)

- [x] 3.1 Add `"userId": "ssc"` to the plugin options in
      `~/.config/opencode/opencode.json`, `opencode service restart`, then
      verify `opencode mcp list` shows `✓ mem0 connected` and
      `mem0_get_status` stays healthy.

## Follow-up

- [x] 3.2 Archive the change, sync nothing (skip_specs), commit docs + code +
      archive, and push to `origin/main`.

## Workflow follow-up

- Archive after review; commit packaging + README edits together with the
  archive.