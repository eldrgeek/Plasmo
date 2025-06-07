#!/bin/bash

# Stop All Development Services
echo "🛑 Stopping All Development Services"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
}

# Stop by PID if available
if [ -f ".service_pids" ]; then
    print_status "📋 Found service PIDs file, stopping services..."
    source .service_pids
    
    if [ ! -z "$MCP_PID" ]; then
        if kill -0 $MCP_PID 2>/dev/null; then
            kill $MCP_PID
            print_status "✅ Stopped MCP Server (PID: $MCP_PID)"
        else
            print_warning "⚠️  MCP Server (PID: $MCP_PID) was not running"
        fi
    fi
    
    if [ ! -z "$SOCKETIO_PID" ]; then
        if kill -0 $SOCKETIO_PID 2>/dev/null; then
            kill $SOCKETIO_PID
            print_status "✅ Stopped SocketIO Server (PID: $SOCKETIO_PID)"
        else
            print_warning "⚠️  SocketIO Server (PID: $SOCKETIO_PID) was not running"
        fi
    fi
    
    if [ ! -z "$PLASMO_PID" ]; then
        if kill -0 $PLASMO_PID 2>/dev/null; then
            kill $PLASMO_PID
            print_status "✅ Stopped Plasmo Dev Server (PID: $PLASMO_PID)"
        else
            print_warning "⚠️  Plasmo Dev Server (PID: $PLASMO_PID) was not running"
        fi
    fi
    
    if [ ! -z "$TEST_RUNNER_PID" ]; then
        if kill -0 $TEST_RUNNER_PID 2>/dev/null; then
            kill $TEST_RUNNER_PID
            print_status "✅ Stopped Continuous Test Runner (PID: $TEST_RUNNER_PID)"
        else
            print_warning "⚠️  Continuous Test Runner (PID: $TEST_RUNNER_PID) was not running"
        fi
    fi
    
    rm .service_pids
else
    print_warning "⚠️  No PID file found, stopping by process name..."
fi

# Fallback: Stop by process patterns
print_status "🧹 Cleaning up any remaining processes..."

# Stop MCP Server
MCP_PIDS=$(pgrep -f "python.*mcp_server.py" 2>/dev/null || true)
if [ ! -z "$MCP_PIDS" ]; then
    echo $MCP_PIDS | xargs kill 2>/dev/null || true
    print_status "✅ Stopped MCP Server processes"
fi

# Stop SocketIO Server and nodemon
SOCKETIO_PIDS=$(pgrep -f "node.*socketio_server.js" 2>/dev/null || true)
if [ ! -z "$SOCKETIO_PIDS" ]; then
    echo $SOCKETIO_PIDS | xargs kill 2>/dev/null || true
    print_status "✅ Stopped SocketIO Server processes"
fi

NODEMON_PIDS=$(pgrep -f "nodemon.*socketio_server.js" 2>/dev/null || true)
if [ ! -z "$NODEMON_PIDS" ]; then
    echo $NODEMON_PIDS | xargs kill 2>/dev/null || true
    print_status "✅ Stopped nodemon processes"
fi

# Stop Plasmo Dev Server
PLASMO_PIDS=$(pgrep -f "node.*plasmo.*dev" 2>/dev/null || true)
if [ ! -z "$PLASMO_PIDS" ]; then
    echo $PLASMO_PIDS | xargs kill 2>/dev/null || true
    print_status "✅ Stopped Plasmo Dev Server processes"
fi

# Stop Continuous Test Runner
TEST_RUNNER_PIDS=$(pgrep -f "python.*continuous_test_runner.py" 2>/dev/null || true)
if [ ! -z "$TEST_RUNNER_PIDS" ]; then
    echo $TEST_RUNNER_PIDS | xargs kill 2>/dev/null || true
    print_status "✅ Stopped Continuous Test Runner processes"
fi

# Stop watchmedo processes
WATCH_PIDS=$(pgrep -f "watchmedo.*mcp_server.py" 2>/dev/null || true)
if [ ! -z "$WATCH_PIDS" ]; then
    echo $WATCH_PIDS | xargs kill 2>/dev/null || true
    print_status "✅ Stopped watchmedo processes"
fi

sleep 2

print_status "🎉 All services stopped!"
echo ""
print_status "📊 Verifying cleanup..."

# Verify no processes are still running
REMAINING=$(pgrep -f "(mcp_server\.py|socketio_server\.js|plasmo.*dev|nodemon.*socketio|watchmedo.*mcp)" 2>/dev/null || true)
if [ -z "$REMAINING" ]; then
    print_status "✅ All processes cleaned up successfully"
else
    print_warning "⚠️  Some processes may still be running:"
    ps aux | grep -E "(mcp_server\.py|socketio_server\.js|plasmo.*dev|nodemon.*socketio|watchmedo.*mcp)" | grep -v grep || true
fi

echo ""
print_status "🚀 To restart all services, run: ./start_all_services.sh" 