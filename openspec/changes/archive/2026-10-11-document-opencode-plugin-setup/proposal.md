# Proposal

## Why

The adapter installs and works, but the concrete "install and configure the
plugin on a new machine" procedure is scattered: the one-line
`opencode plugin add` sits in the root README, the option mapping and
`serverCommand` tuning sit in the adapter README, and the restart/verify and
proxy caveats live only in conversation. A newcomer who runs the one-liner does
not know to set hub options through the object form, restart the service, or
verify the connection. This documents the whole path from a bare machine to
`mem0 connected` in one ordered walkthrough.

## What Changes

- Add a step-by-step **Setup** walkthrough to
  `integrations/opencode/README.md` covering: the `uv` prerequisite, the
  recommended server pre-install, `opencode plugin add`, converting the entry to
  the object form with options in `opencode.json`, `opencode service restart`,
  and verifying with `opencode mcp list`.
- Cross-reference the existing startup-latency and proxy-environment guidance
  from those steps so the fast-start remedy and the `NO_PROXY` note are reachable
  in context.
- Add a concise version of the same flow to the root README's
  "Client Integrations -> OpenCode" section, linking to the adapter README for
  the details.
- Documentation only. No code changes and no spec-level behavior change
  (`skip_specs`).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

<!-- none: documentation only -->

## Impact

- `integrations/opencode/README.md`
- root `README.md`
