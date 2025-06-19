#!/bin/bash

echo "🚀 Starting FastMCP Server for Cursor (HTTP Mode)..."
echo "====================================================="

# Check if the server file exists
if [ ! -f "mcp_server.py" ]; then
    echo "❌ mcp_server.py not found in current directory"
    echo "Please run this script from the directory containing mcp_server.py"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import fastmcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed. Running setup first..."
    ./setup_mcp.sh
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Please install dependencies manually:"
        echo "   pip3 install fastmcp"
        exit 1
    fi
fi

echo "✅ Dependencies verified"
echo "🌐 Starting server in HTTP mode on http://127.0.0.1:8000/mcp"
echo "🔄 Auto-reload enabled - watching mcp_server.py for changes"
echo ""
echo "📝 Transport Modes Available:"
echo "   🖥️  HTTP (this script):   ./start_mcp.sh"
echo "   📟  STDIO (Claude Desktop): ./start_mcp_stdio.sh"
echo ""
echo "📝 Make sure to configure Cursor with the MCP server settings"
echo "   (see mcp_server.py for configuration details)"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

# Function to start the server
start_server() {
    echo "$(date '+%H:%M:%S') 🟢 Starting MCP server..."
    python3 mcp_server.py &
    SERVER_PID=$!
    echo "$(date '+%H:%M:%S') 📡 Server started with PID: $SERVER_PID"
}

# Function to stop the server
stop_server() {
    if [ ! -z "$SERVER_PID" ] && kill -0 $SERVER_PID 2>/dev/null; then
        echo "$(date '+%H:%M:%S') 🔴 Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null
        echo "$(date '+%H:%M:%S') ✅ Server stopped"
    fi
}

# Function to restart the server
restart_server() {
    echo "$(date '+%H:%M:%S') 🔄 File change detected - restarting server..."
    stop_server
    sleep 1
    start_server
    echo "$(date '+%H:%M:%S') ✨ Server reloaded successfully!"
    echo ""
}

# Cleanup function
cleanup() {
    echo ""
    echo "$(date '+%H:%M:%S') 🛑 Shutting down..."
    stop_server
    if [ ! -z "$WATCHER_PID" ] && kill -0 $WATCHER_PID 2>/dev/null; then
        kill $WATCHER_PID 2>/dev/null
    fi
    echo "$(date '+%H:%M:%S') 👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the server initially
start_server

# Check for file watching tools and start appropriate watcher
if command -v fswatch >/dev/null 2>&1; then
    # Use fswatch (macOS/Linux)
    echo "$(date '+%H:%M:%S') 👁️  Using fswatch for file monitoring"
    fswatch -o mcp_server.py | while read f; do restart_server; done &
    WATCHER_PID=$!
elif command -v inotifywait >/dev/null 2>&1; then
    # Use inotifywait (Linux)
    echo "$(date '+%H:%M:%S') 👁️  Using inotifywait for file monitoring"
    while inotifywait -e modify mcp_server.py; do restart_server; done &
    WATCHER_PID=$!
else
    # Fallback: simple polling method
    echo "$(date '+%H:%M:%S') 👁️  Using polling method for file monitoring"
    echo "$(date '+%H:%M:%S') 💡 For better performance, install fswatch: brew install fswatch"
    
    # Get initial modification time
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LAST_MOD=$(stat -f %m mcp_server.py)
    else
        LAST_MOD=$(stat -c %Y mcp_server.py)
    fi
    
    # Polling loop
    while true; do
        sleep 2
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CURRENT_MOD=$(stat -f %m mcp_server.py)
        else
            CURRENT_MOD=$(stat -c %Y mcp_server.py)
        fi
        
        if [ "$CURRENT_MOD" != "$LAST_MOD" ]; then
            LAST_MOD=$CURRENT_MOD
            restart_server
        fi
    done &
    WATCHER_PID=$!
fi

echo "$(date '+%H:%M:%S') 🎯 Auto-reload is active!"
echo "$(date '+%H:%M:%S') 📝 Edit mcp_server.py and save to see auto-reload in action"
echo "$(date '+%H:%M:%S') ⚡ File watcher PID: $WATCHER_PID"
echo ""

# Wait for the server process
wait $SERVER_PID 