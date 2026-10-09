#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
TRANSPORT="stdio"
PORT=8050
USE_ENV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)  CONFIG_FILE="$2"; shift 2 ;;
        --transport) TRANSPORT="$2"; shift 2 ;;
        --port)    PORT="$2"; shift 2 ;;
        --env)     USE_ENV=true; shift ;;
        -h|--help)
            echo "Usage: ./start.sh [options]"
            echo ""
            echo "Options:"
            echo "  --config PATH    Path to config file (default: ./config.json)"
            echo "  --transport MODE Transport mode: stdio (default) or sse"
            echo "  --port PORT      Port for SSE mode (default: 8050)"
            echo "  --env            Use environment variables (MEM0_HOST, MEM0_USER_ID, etc.)"
            echo "                     Supports MEM0_INFER (default: false)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.8+."
    exit 1
fi

if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

source "$SCRIPT_DIR/.venv/bin/activate"

if [ "$USE_ENV" = true ]; then
    python3 "$SCRIPT_DIR/mem0_mcp_server.py" --transport "$TRANSPORT" --port "$PORT" --env
else
    python3 "$SCRIPT_DIR/mem0_mcp_server.py" --config "$CONFIG_FILE" --transport "$TRANSPORT" --port "$PORT"
fi
