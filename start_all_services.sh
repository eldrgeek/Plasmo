Test auto-restart system working
#!/bin/bash

# Start All Development Services with Auto-Restart
# This script starts MCP server, Plasmo dev, and SocketIO server with file watching

echo "🚀 Starting All Development Services"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

# Check if required files exist
if [ ! -f "mcp_server.py" ]; then
    print_error "❌ mcp_server.py not found!"
    exit 1
fi

if [ ! -f "socketio_server.js" ]; then
    print_error "❌ socketio_server.js not found!"
    exit 1
fi

if [ ! -f "package.json" ]; then
    print_error "❌ package.json not found!"
    exit 1
fi

# Install nodemon if not present for auto-restart
if ! command -v nodemon &> /dev/null; then
    print_warning "⚠️  nodemon not found, installing for auto-restart..."
    pnpm add -D nodemon
fi

# Kill any existing services
print_info "🧹 Cleaning up existing services..."
pkill -f "python.*mcp_server.py" 2>/dev/null || true
pkill -f "node.*socketio_server.js" 2>/dev/null || true
pkill -f "node.*plasmo.*dev" 2>/dev/null || true

sleep 2

# Create log directory
mkdir -p logs

# Function to start MCP server with auto-restart
start_mcp_server() {
    print_status "🐍 Starting MCP Server with auto-restart..."
    
    # Use watchmedo for Python file watching if available
    if command -v watchmedo &> /dev/null; then
        watchmedo auto-restart --patterns="*.py" --recursive --directory="." -- \
            python3 mcp_server.py > logs/mcp_server.log 2>&1 &
        MCP_PID=$!
        print_status "✅ MCP Server started with file watching (PID: $MCP_PID)"
    else
        # Fallback to simple restart
        python3 mcp_server.py > logs/mcp_server.log 2>&1 &
        MCP_PID=$!
        print_status "✅ MCP Server started (PID: $MCP_PID)"
        print_warning "⚠️  Install watchdog for auto-restart: pip install watchdog"
    fi
}

# Function to start SocketIO server with auto-restart
start_socketio_server() {
    print_status "🌐 Starting SocketIO Server with auto-restart..."
    
    nodemon --watch socketio_server.js --watch cursor_ai_injector.py \
        --exec "node socketio_server.js" > logs/socketio_server.log 2>&1 &
    SOCKETIO_PID=$!
    print_status "✅ SocketIO Server started with file watching (PID: $SOCKETIO_PID)"
}

# Function to start Plasmo dev server
start_plasmo_dev() {
    print_status "🎯 Starting Plasmo Dev Server..."
    
    pnpm dev > logs/plasmo_dev.log 2>&1 &
    PLASMO_PID=$!
    print_status "✅ Plasmo Dev Server started (PID: $PLASMO_PID)"
}

# Function to start Continuous Test Runner
start_test_runner() {
    print_status "🧪 Starting Continuous Test Runner..."
    
    python3 continuous_test_runner.py > logs/continuous_testing.log 2>&1 &
    TEST_RUNNER_PID=$!
    print_status "✅ Continuous Test Runner started (PID: $TEST_RUNNER_PID)"
}

# Start all services
print_info "🚀 Starting all services..."

start_mcp_server
sleep 2

start_socketio_server  
sleep 2

start_plasmo_dev
sleep 3

start_test_runner
sleep 2

# Display status
echo ""
print_status "🎉 All Services Started!"
echo "================================"
print_info "📊 Service Status:"
echo "  • MCP Server (PID: $MCP_PID) - http://localhost:8000"
echo "  • SocketIO Server (PID: $SOCKETIO_PID) - http://localhost:3001" 
echo "  • Plasmo Dev Server (PID: $PLASMO_PID) - Auto-reload enabled"
echo "  • Continuous Test Runner (PID: $TEST_RUNNER_PID) - Auto-testing enabled"
echo ""
print_info "📁 Log Files:"
echo "  • MCP Server: logs/mcp_server.log"
echo "  • SocketIO Server: logs/socketio_server.log"
echo "  • Plasmo Dev: logs/plasmo_dev.log"
echo "  • Continuous Testing: logs/continuous_testing.log"
echo ""
print_info "🔧 Auto-Restart Enabled For:"
echo "  • MCP Server: *.py files (if watchdog installed)"
echo "  • SocketIO Server: socketio_server.js, cursor_ai_injector.py"
echo "  • Plasmo Dev: Built-in hot reload"
echo "  • Test Runner: *.ts, *.tsx, *.js, *.jsx, *.html, *.css, *.py files"
echo ""

# Save PIDs for cleanup script
echo "MCP_PID=$MCP_PID" > .service_pids
echo "SOCKETIO_PID=$SOCKETIO_PID" >> .service_pids  
echo "PLASMO_PID=$PLASMO_PID" >> .service_pids
echo "TEST_RUNNER_PID=$TEST_RUNNER_PID" >> .service_pids

print_info "🛑 To stop all services, run: ./stop_all_services.sh"
print_info "📊 To check status, run: ./check_services.sh"

# Wait and monitor (optional)
if [ "$1" = "--monitor" ]; then
    print_info "👀 Monitoring services (Ctrl+C to exit)..."
    echo ""
    
    while true; do
        sleep 5
        
        # Check if services are still running
        if ! kill -0 $MCP_PID 2>/dev/null; then
            print_error "❌ MCP Server stopped unexpectedly"
            start_mcp_server
        fi
        
        if ! kill -0 $SOCKETIO_PID 2>/dev/null; then
            print_error "❌ SocketIO Server stopped unexpectedly"  
            start_socketio_server
        fi
        
        if ! kill -0 $PLASMO_PID 2>/dev/null; then
            print_error "❌ Plasmo Dev Server stopped unexpectedly"
            start_plasmo_dev
        fi
    done
fi

echo ""
print_status "🚀 All services are running in the background!"
print_info "💡 Access the web interfaces:"
echo "  • SocketIO Controller: http://localhost:3001"
echo "  • MCP Server Health: http://localhost:8000/health" 