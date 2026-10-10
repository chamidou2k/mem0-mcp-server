/**
 * Plugin options supplied by OpenCode's object-form plugin entry. Declared
 * locally, along with the structural views below, so the compiled module has
 * no runtime imports and therefore loads from wherever the installer places
 * it (a Git-installed plugin cannot resolve OpenCode's own packages).
 */
type PluginOptions = Readonly<Record<string, unknown>>;
/** Minimal structural view of the OpenCode V2 MCP editor. */
interface McpEditor {
    set(name: string, server: {
        type: "local";
        command: string[];
        environment: Record<string, string>;
        disabled: boolean;
    }): void;
}
/** Minimal structural view of the OpenCode V2 plugin setup context. */
interface PluginContext {
    readonly options?: PluginOptions;
    readonly mcp: {
        transform(edit: (editor: McpEditor) => void): Promise<void>;
    };
}
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
    setup: (context: PluginContext) => Promise<void>;
};
export default _default;
