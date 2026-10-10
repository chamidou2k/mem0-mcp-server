# opencode-mem0-mcp

An OpenCode plugin that registers the [Mem0 MCP Server](../../) as a local MCP
server named `mem0`, giving OpenCode persistent memory backed by your mem0 hub.

## Install

Install the plugin straight from the project repository (it lives in the
`integrations/opencode` subdirectory):

```bash
opencode plugin add 'github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode'
```

Or list it in the `plugins` array of `opencode.json`:

```json
{
  "plugins": [
    "github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode"
  ]
}
```

A single install is enough: by default the plugin launches the server with
`uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server`,
which downloads and runs the companion Python server on demand.

## Prerequisite

The default launch command uses [`uv`](https://docs.astral.sh/uv/), so install
it first if you do not have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you prefer not to use `uv`, install the server yourself and point the plugin
at it with the `serverCommand` option:

```bash
pip install "git+https://github.com/chamidou2k/mem0-mcp-server"
```

```json
{ "serverCommand": "mem0-mcp-server" }
```

## Configure

Add the plugin to your OpenCode configuration (`opencode.json`). OpenCode V2
reads the `plugins` array; pass the options through the object form:

```json
{
  "plugins": [
    {
      "package": "github:chamidou2k/mem0-mcp-server#main::path:integrations/opencode",
      "options": {
        "mem0Host": "http://192.168.1.100:8001",
        "mem0HostHttps": "https://192.168.1.100:8443",
        "certPath": "/path/to/ca-certificate.pem",
        "tlsVerifyHostname": false,
        "apiKey": "change-me",
        "userId": "opencode",
        "agentId": "opencode",
        "channel": "",
        "searchThreshold": 0.1,
        "maxMemories": 50,
        "infer": true
      }
    }
  ]
}
```

OpenCode V1 reads the `plugin` array with a `[package, options]` tuple:

```json
{
  "plugin": [
    ["opencode-mem0-mcp", { "mem0Host": "http://192.168.1.100:8001", "apiKey": "change-me" }]
  ]
}
```

Every option is optional. An omitted option falls back to the same-named
environment variable and, when that is also unset, to the server's own default.

### Options

| Plugin option | Environment variable | Description |
|---|---|---|
| `mem0Host` | `MEM0_HOST` | Preferred HTTP hub URL |
| `mem0HostHttps` | `MEM0_HOST_HTTPS` | HTTPS hub URL (fallback, or HTTPS-only) |
| `certPath` | `MEM0_CERT_PATH` | CA certificate/bundle verifying the HTTPS hub |
| `tlsVerifyHostname` | `MEM0_TLS_VERIFY_HOSTNAME` | Verify the hub cert's hostname/IP (default `true`) |
| `apiKey` | `MEM0_API_KEY` | API key sent as the `X-API-Key` header |
| `userId` | `MEM0_USER_ID` | Mem0 user identifier |
| `agentId` | `MEM0_AGENT_ID` | Mem0 agent identifier |
| `channel` | `MEM0_CHANNEL` | Channel/source identifier |
| `searchThreshold` | `MEM0_SEARCH_THRESHOLD` | Similarity threshold (0.0-1.0) |
| `maxMemories` | `MEM0_MAX_MEMORIES` | Max results for list/search |
| `infer` | `MEM0_INFER` | Enable semantic fact extraction |
| `serverCommand` | *(none)* | Override the server launch command (a string or an array of strings); defaults to `uvx --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server` |

## Startup latency

When OpenCode connects MCP servers for several workspace directories at once, it
starts one server process per directory. The first `uvx` run must resolve and
build the server environment, and concurrent runs serialize on uv's cache lock.
On a cold cache some connections can therefore exceed OpenCode's MCP connect
timeout (~30s) and show `mem0` as pending or failed.

Install the server once as a uv tool and point `serverCommand` at the resulting
binary to make every start fast and lock-free:

```bash
uv tool install --from git+https://github.com/chamidou2k/mem0-mcp-server mem0-mcp-server
```

```json
{ "serverCommand": ["/home/you/.local/bin/mem0-mcp-server"] }
```

With a warm cache the `uvx` default also starts in about two seconds, so this
tuning is only needed for multi-directory setups or slow networks.

## How it works

The default export supports both plugin APIs and imports nothing at runtime, so
it loads from wherever OpenCode installs it. On OpenCode V2 the module exports
an `id` and a `setup`; `setup` registers the server through the MCP editor and
reads options from `ctx.options`:

```ts
await ctx.mcp.transform((editor) => {
  editor.set("mem0", {
    type: "local",
    command: [
      "uvx", "--from",
      "git+https://github.com/chamidou2k/mem0-mcp-server",
      "mem0-mcp-server",
    ],
    environment: { /* the MEM0_* variables above */ },
    disabled: false,
  });
});
```

On OpenCode V1 the `server` hook registers the same server through the
configuration hook:

```jsonc
config.mcp["mem0"] = {
  "type": "local",
  "command": [
    "uvx", "--from",
    "git+https://github.com/chamidou2k/mem0-mcp-server",
    "mem0-mcp-server"
  ],
  "environment": { /* the MEM0_* variables above */ },
  "enabled": true
}
```

Both paths forward the same environment, so the hub connection options reach the
server as environment variables - no configuration file or secrets are written
to disk.

## Development

The adapter ships prebuilt, so installing from Git needs no build. Maintainers
build from the repository root (the build tooling lives in the root manifest):

```bash
npm install
npx tsc -p integrations/opencode
```

Commit the regenerated `dist/` whenever `src/` changes.
