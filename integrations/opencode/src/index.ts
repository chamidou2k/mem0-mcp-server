import { Plugin } from "@opencode/plugin";
import type { PluginOptions } from "@opencode/plugin";

/**
 * Maps each supported plugin option to the environment variable the
 * `mem0-mcp-server` process reads. The server treats unset variables as
 * "not configured" and applies its own defaults, so the adapter only forwards
 * the options the user actually supplied.
 */
const OPTION_ENV_MAP: Record<string, string> = {
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

/** Name under which the mem0 server is registered with OpenCode. */
const MCP_SERVER_NAME = "mem0";

/** Repository the default launch command installs the server from. */
const SERVER_REPOSITORY = "git+https://github.com/chamidou2k/mem0-mcp-server";

/**
 * Default launch command. `uvx` installs and runs the server straight from the
 * project repository, so installing only this plugin also provides the server.
 */
const DEFAULT_SERVER_COMMAND = [
  "uvx",
  "--from",
  SERVER_REPOSITORY,
  "mem0-mcp-server",
];

/** Plugin option that overrides the default launch command. */
const SERVER_COMMAND_OPTION = "serverCommand";

/** Normalize a string or string-array command option to a command array. */
function toCommand(value: unknown): string[] | undefined {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed === "" ? undefined : [trimmed];
  }
  if (Array.isArray(value)) {
    const parts = value.filter(
      (part): part is string => typeof part === "string" && part.trim() !== "",
    );
    return parts.length > 0 ? parts : undefined;
  }
  return undefined;
}

/**
 * Resolve the server launch command: the `serverCommand` option when supplied,
 * otherwise the default `uvx` command that installs the server from the
 * project repository.
 */
function resolveServerCommand(options?: PluginOptions): string[] {
  return toCommand(options?.[SERVER_COMMAND_OPTION]) ?? DEFAULT_SERVER_COMMAND;
}

/** Stable plugin id shared by the V1 and V2 entry points. */
const PLUGIN_ID = "opencode-mem0-mcp";

/** Normalize an option value to the string form the server expects. */
function toEnvValue(value: unknown): string | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (typeof value === "number") {
    return String(value);
  }
  if (typeof value === "string") {
    return value.trim() === "" ? undefined : value;
  }
  return undefined;
}

/**
 * Build the environment for the server process from the plugin options,
 * falling back to an already-set process environment variable when the option
 * was not supplied. Options left unset are omitted so the server default wins.
 */
function buildEnvironment(options?: PluginOptions): Record<string, string> {
  const environment: Record<string, string> = {};
  for (const [option, envVar] of Object.entries(OPTION_ENV_MAP)) {
    const value = toEnvValue(options?.[option]) ?? toEnvValue(process.env[envVar]);
    if (value !== undefined) {
      environment[envVar] = value;
    }
  }
  return environment;
}

/**
 * OpenCode V2 entry point. OpenCode loads a plugin that default-exports a
 * `Plugin.define({ id, setup })` module and calls `setup` once at boot. The
 * MCP server is registered through the MCP editor so the entry lands wherever
 * the running OpenCode stores local servers (`mcp.servers`).
 */
const v2Plugin = Plugin.define({
  id: PLUGIN_ID,
  async setup(context) {
    await context.mcp.transform((editor) => {
      editor.set(MCP_SERVER_NAME, {
        type: "local",
        command: resolveServerCommand(context.options),
        environment: buildEnvironment(context.options),
        disabled: false,
      });
    });
  },
});

/** Minimal structural types for the OpenCode V1 plugin API. */
interface V1Config {
  mcp?: Record<string, unknown>;
}
interface V1Hooks {
  config?: (config: V1Config) => Promise<void>;
}

/**
 * OpenCode V1 entry point. V1 loads a default export shaped like
 * `{ id, server }` and calls `server` to obtain hooks; the `config` hook
 * mutates the `mcp.<name>` entry directly. V1 uses `enabled` (V2 uses
 * `disabled`).
 */
const server = async (
  _input: unknown,
  options?: PluginOptions,
): Promise<V1Hooks> => ({
  config: async (config) => {
    config.mcp ??= {};
    config.mcp[MCP_SERVER_NAME] = {
      type: "local",
      command: resolveServerCommand(options),
      environment: buildEnvironment(options),
      enabled: true,
    };
  },
});

/**
 * Default export supporting both plugin APIs: V2 reads `setup` (from
 * `Plugin.define`), V1 reads `server`.
 */
export default {
  ...v2Plugin,
  server,
};
