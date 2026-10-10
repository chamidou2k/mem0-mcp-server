import { Plugin } from "@opencode/plugin";
import type { PluginOptions } from "@opencode/plugin";
/** Minimal structural types for the OpenCode V1 plugin API. */
interface V1Config {
    mcp?: Record<string, unknown>;
}
interface V1Hooks {
    config?: (config: V1Config) => Promise<void>;
}
/**
 * Default export supporting both plugin APIs: V2 reads `setup` (from
 * `Plugin.define`), V1 reads `server`.
 */
declare const _default: {
    server: (_input: unknown, options?: PluginOptions) => Promise<V1Hooks>;
    id: string;
    setup: (context: Plugin.Context) => Promise<Plugin.Cleanup | void> | Plugin.Cleanup | void;
};
export default _default;
