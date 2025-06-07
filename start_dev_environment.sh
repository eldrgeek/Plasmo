#!/bin/bash

# Plasmo Extension Development Environment Startup Script with Auto-Restart
# This script starts both the MCP server and Plasmo dev server
# The MCP server automatically restarts when source files change

echo "🚀 Starting Plasmo Development Environment with Auto-Restart"
echo "============================================================="

# Global variables
MCP_PID=""
PLASMO_PID=""
WATCHER_PID=""

# Files to watch for MCP server changes
MCP_WATCH_FILES=(
    "mcp_server.py"
    "chrome_debug_fixes.py"
    "requirements.txt"
)

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development environment..."
    
    # Kill all child processes
    if [ ! -z "$WATCHER_PID" ]; then
        kill $WATCHER_PID 2>/dev/null
    fi
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
    fi
    if [ ! -z "$PLASMO_PID" ]; then
        kill $PLASMO_PID 2>/dev/null
    fi
    
    # Cleanup any remaining processes
    pkill -f "mcp_server.py" 2>/dev/null
    pkill -f "pnpm.*dev" 2>/dev/null
    
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if pnpm is available
if ! command -v pnpm &> /dev/null; then
    echo "❌ Error: pnpm is not installed or not in PATH"
    echo "   Install with: npm install -g pnpm"
    exit 1
fi

# Check if MCP server file exists
if [ ! -f "mcp_server.py" ]; then
    echo "❌ Error: mcp_server.py not found"
    exit 1
fi

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Function to start MCP server
start_mcp_server() {
    if [ ! -z "$MCP_PID" ]; then
        echo "🔄 Stopping existing MCP server (PID: $MCP_PID)..."
        kill $MCP_PID 2>/dev/null
        sleep 2
    fi
    
    echo "🔧 Starting Consolidated MCP Server v2.0..."
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
echo "   Watching: ${MCP_WATCH_FILES[*]}"
echo ""

# Start Plasmo dev server in background
echo "🎯 Starting Plasmo dev server..."
pnpm dev &
PLASMO_PID=$!

# Wait a moment for Plasmo to start
sleep 3

# Check if Plasmo started successfully
if ! kill -0 $PLASMO_PID 2>/dev/null; then
    echo "❌ Failed to start Plasmo dev server"
    cleanup
    exit 1
fi

echo "✅ Plasmo dev server started (PID: $PLASMO_PID)"
echo ""

echo "🎉 Development environment is ready with auto-restart!"
echo "======================================================"
echo "📡 MCP Server: http://127.0.0.1:8000/mcp (auto-restart enabled)"
echo "🌐 Plasmo Extension: Watch console for dev server URL"
echo "🔧 Chrome Debug: Run ./launch-chrome-debug.sh for debugging"
echo "👁️  File Watcher: Monitoring MCP server files for changes"
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
echo "Press Ctrl+C to stop all services..."

# Wait for background processes (Plasmo and file watcher)
wait 