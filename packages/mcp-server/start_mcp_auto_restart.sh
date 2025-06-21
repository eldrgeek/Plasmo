#!/bin/bash

# MCP Server Auto-Restart Script
# Monitors MCP server files and automatically restarts on changes

echo "🔧 Starting MCP Server with Auto-Restart"
echo "========================================"

# Global variables
MCP_PID=""
WATCHER_PID=""

# Files to watch for MCP server changes
MCP_WATCH_FILES=(
    "mcp_server.py"
    "requirements.txt"
)

# Lock file to prevent multiple instances
LOCK_FILE="/tmp/mcp_auto_restart.lock"
LOCK_PID_FILE="/tmp/mcp_auto_restart.pid"

# Function to check if another instance is running
is_already_running() {
    if [ -f "$LOCK_PID_FILE" ]; then
        local existing_pid=$(cat "$LOCK_PID_FILE" 2>/dev/null)
        if [ ! -z "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
            # Check if it's actually our script
            if ps -p "$existing_pid" -o comm= | grep -q "bash"; then
                return 0
            fi
        fi
    fi
    return 1
}

# Function to create lock
create_lock() {
    echo $$ > "$LOCK_PID_FILE"
    touch "$LOCK_FILE"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping MCP Server and file watcher..."
    
    if [ ! -z "$WATCHER_PID" ]; then
        kill $WATCHER_PID 2>/dev/null
    fi
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
    fi
    
    pkill -f "mcp_server.py" 2>/dev/null
    
    # Remove lock files
    rm -f "$LOCK_FILE" "$LOCK_PID_FILE" 2>/dev/null
    
    echo "✅ MCP Server stopped"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Function to start MCP server
start_mcp_server() {
    if [ ! -z "$MCP_PID" ]; then
        echo "🔄 Stopping existing MCP server (PID: $MCP_PID)..."
        kill $MCP_PID 2>/dev/null
        sleep 2
    fi
    
    echo "🚀 Starting Consolidated MCP Server v2.0..."
    python3 mcp_server.py --port 8000 &
    MCP_PID=$!
    
    # Wait a moment for MCP server to start
    sleep 3
    
    # Check if MCP server started successfully
    if ! kill -0 $MCP_PID 2>/dev/null; then
        echo "❌ Failed to start MCP server"
        return 1
    fi
    
    echo "✅ MCP Server started (PID: $MCP_PID)"
    echo "   Available at: http://127.0.0.1:8000/mcp"
    return 0
}

# Function to get file modification times
get_file_timestamps() {
    local timestamps=""
    for file in "${MCP_WATCH_FILES[@]}"; do
        if [ -f "$file" ]; then
            local mtime=$(stat -f "%m" "$file" 2>/dev/null || echo "0")
            timestamps="$timestamps:$mtime"
        fi
    done
    echo "$timestamps"
}

# Function to watch for file changes and restart MCP server
watch_and_restart() {
    local last_timestamps=$(get_file_timestamps)
    
    while true; do
        sleep 2  # Check every 2 seconds
        
        local current_timestamps=$(get_file_timestamps)
        
        if [ "$current_timestamps" != "$last_timestamps" ]; then
            echo ""
            echo "📁 File changes detected - restarting MCP server..."
            if start_mcp_server; then
                echo "🔄 MCP Server restarted successfully"
            else
                echo "❌ Failed to restart MCP server"
            fi
            echo ""
            last_timestamps="$current_timestamps"
        fi
    done
}

# Check if another instance is already running
if is_already_running; then
    echo "✅ MCP auto-restart script is already running (PID: $(cat "$LOCK_PID_FILE"))"
    echo "   No need to start another instance."
    exit 0
fi

# Create lock to prevent multiple instances
create_lock

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH"
    exit 1
fi

if [ ! -f "mcp_server.py" ]; then
    echo "❌ Error: mcp_server.py not found"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Start MCP Server initially
start_mcp_server
if [ $? -ne 0 ]; then
    echo "❌ Failed to start MCP server initially"
    exit 1
fi

# Start file watcher in background
echo "👁️  Starting file watcher for auto-restart..."
watch_and_restart &
WATCHER_PID=$!
echo "✅ File watcher started (PID: $WATCHER_PID)"

echo ""
echo "📝 Auto-restart will trigger when these files change:"
for file in "${MCP_WATCH_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (not found)"
    fi
done

echo ""
echo "🎯 MCP Server is running with auto-restart enabled!"
echo "   Press Ctrl+C to stop the server and watcher..."
echo ""

# Wait for background processes
wait 