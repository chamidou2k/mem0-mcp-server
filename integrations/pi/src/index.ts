/**
 * pi extension: registers the mem0 MCP server as a local stdio MCP server
 * named `mem0`, giving pi persistent memory backed by your mem0 hub.
 *
 * pi registers MCP servers directly through its MCP configuration
 * (`pi mcp add <server> -- <command>`), so this extension's role is to
 * surface the mem0 server specification and default launch command that
 * `pi mcp add` consumes. The compiled module imports nothing at runtime so
 * it loads from wherever pi installs it (a Git-installed extension cannot
 * resolve pi's own packages).
 */

type McpServer = Readonly<{
  type: "local";
  command: string[];
  environment: Record<string, string>;
  disabled: boolean;
}>;

/** Name under which the mem0 server is registered with pi. */
export const MCP_SERVER_NAME = "mem0";

/** Repository the default launch command installs the server from. */
export const SERVER_REPOSITORY = "git+https://github.com/chamidou2k/mem0-mcp-server";

/**
 * Default launch command. `uvx` installs and runs the server straight from
 * the project repository, so installing only this extension also provides
 * the server.
 */
export const DEFAULT_SERVER_COMMAND: readonly string[] = [
  "uvx",
  "--from",
  SERVER_REPOSITORY,
  "mem0-mcp-server",
];

/** Extension option that overrides the default launch command. */
export const SERVER_COMMAND_OPTION = "serverCommand";

/**
 * Maps each supported extension option to the environment variable the
 * `mem0-mcp-server` process reads. The server treats unset variables as
 * "not configured" and applies its own defaults, so the extension only
 * forwards the options the user actually supplied.
 */
export const OPTION_ENV_MAP: Readonly<Record<string, string>> = {
  mem0Host: "MEM0_HOST",
  mem0HostHttps: "MEM0_HOST_HTTPS",
  certPath: "MEM0_CERT_PATH",
  tlsVerifyHostname: "MEM0_TLS_VERIFY_HOSTNAME",
  apiKey: "MEM0_API_KEY",
  userId: "MEM0_USER_ID",
  agentId: "MEM0_AGENT_ID",
  channel: "MEM0_CHANNEL",
  searchThreshold: "MEM0_SEARCH_THRESHOLD",
  maxMemories: "MEM0_MAX_MEMORIES",
  infer: "MEM0_INFER",
};

/**
 * Build the mem0 MCP server specification that `pi mcp add mem0 -- ...`
 * consumes. The `command` is the `serverCommand` option when supplied,
 * otherwise the default `uvx` command that installs the server from the
 * project repository.
 */
export function buildServer(command?: string[]): McpServer {
  return {
    type: "local",
    command: command && command.length > 0 ? command : [...DEFAULT_SERVER_COMMAND],
    environment: {},
    disabled: false,
  };
}

export default {
  id: "pi-mem0-mcp",
  buildServer,
};
