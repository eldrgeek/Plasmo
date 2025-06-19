#!/bin/bash

# Script to ensure MCP auto-restart is running
# This can be called by Claude Code to make sure the MCP server is available

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if the auto-restart script is already running
if [ -f "/tmp/mcp_auto_restart.pid" ]; then
    PID=$(cat "/tmp/mcp_auto_restart.pid" 2>/dev/null)
    if [ ! -z "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "✅ MCP auto-restart is already running (PID: $PID)"
        exit 0
    fi
fi

# Start the auto-restart script in the background
echo "🚀 Starting MCP auto-restart script..."
nohup ./start_mcp_auto_restart.sh > /tmp/mcp_auto_restart.log 2>&1 &

# Give it a moment to start
sleep 2

# Check if it started successfully
if [ -f "/tmp/mcp_auto_restart.pid" ]; then
    PID=$(cat "/tmp/mcp_auto_restart.pid" 2>/dev/null)
    if [ ! -z "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "✅ MCP auto-restart started successfully (PID: $PID)"
        echo "   Log file: /tmp/mcp_auto_restart.log"
        exit 0
    fi
fi

echo "❌ Failed to start MCP auto-restart script"
exit 1