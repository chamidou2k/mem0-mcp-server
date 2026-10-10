# opencode-mem0-mcp

An OpenCode plugin that registers the [Mem0 MCP Server](../../) as a local MCP
server named `mem0`, giving OpenCode persistent memory backed by your mem0 hub.

## Install

```bash
opencode plugin add opencode-mem0-mcp
```

The plugin registers a local stdio MCP server named `mem0` that runs the
installed `mem0-mcp-server` command.

## Prerequisite

The plugin launches the `mem0-mcp-server` command, so install the server first:

```bash
pip install mem0-mcp-server
```

Or install it from the repository:

```bash
pip install "git+https://github.com/chamidou2k/mem0-mcp-server"
```

## Configure

Add the plugin to your OpenCode configuration (`opencode.json`). OpenCode V2
reads the `plugins` array; pass the options through the object form:

```json
{
  "plugins": [
    {
      "package": "opencode-mem0-mcp",
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

## How it works

The default export supports both plugin APIs. On OpenCode V2 the plugin is
loaded with `Plugin.define({ id, setup })`; `setup` registers the server through
the MCP editor and reads options from `ctx.options`:

```ts
await ctx.mcp.transform((editor) => {
  editor.set("mem0", {
    type: "local",
    command: ["mem0-mcp-server"],
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
  "command": ["mem0-mcp-server"],
  "environment": { /* the MEM0_* variables above */ },
  "enabled": true
}
```

Both paths forward the same environment, so the hub connection options reach the
server as environment variables - no configuration file or secrets are written
to disk.

## Development

```bash
npm install
npm run build
```
