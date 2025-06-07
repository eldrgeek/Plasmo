#!/bin/bash

# Check Status of All Development Services
echo "📊 Development Services Status"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check MCP Server
print_info "Checking MCP Server..."
MCP_RUNNING=$(pgrep -f "python.*mcp_server.py" 2>/dev/null || true)
if [ ! -z "$MCP_RUNNING" ]; then
    print_status "MCP Server is running (PID: $MCP_RUNNING)"
    
    # Test HTTP endpoint
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "MCP Server HTTP endpoint is responding"
    else
        print_warning "MCP Server process running but HTTP endpoint not responding"
    fi
else
    print_error "MCP Server is not running"
fi

echo ""

# Check SocketIO Server
print_info "Checking SocketIO Server..."
SOCKETIO_RUNNING=$(pgrep -f "node.*socketio_server.js" 2>/dev/null || true)
NODEMON_RUNNING=$(pgrep -f "nodemon.*socketio_server.js" 2>/dev/null || true)

if [ ! -z "$SOCKETIO_RUNNING" ] || [ ! -z "$NODEMON_RUNNING" ]; then
    if [ ! -z "$NODEMON_RUNNING" ]; then
        print_status "SocketIO Server is running with auto-restart (nodemon PID: $NODEMON_RUNNING)"
    else
        print_status "SocketIO Server is running (PID: $SOCKETIO_RUNNING)"
    fi
    
    # Test HTTP endpoint
    if curl -s -f http://localhost:3001/ > /dev/null 2>&1; then
        print_status "SocketIO Server HTTP endpoint is responding"
    else
        print_warning "SocketIO Server process running but HTTP endpoint not responding"
    fi
else
    print_error "SocketIO Server is not running"
fi

echo ""

# Check Plasmo Dev Server
print_info "Checking Plasmo Dev Server..."
PLASMO_RUNNING=$(pgrep -f "node.*plasmo.*dev" 2>/dev/null || true)
if [ ! -z "$PLASMO_RUNNING" ]; then
    print_status "Plasmo Dev Server is running (PID: $PLASMO_RUNNING)"
    
    # Check if build directory exists
    if [ -d "build" ]; then
        print_status "Extension build directory exists"
        
        # Check for recent build
        if [ -d "build/chrome-mv3-dev" ]; then
            print_status "Chrome extension build is available"
        else
            print_warning "Chrome extension build not found"
        fi
    else
        print_warning "Build directory not found"
    fi
else
    print_error "Plasmo Dev Server is not running"
fi

echo ""

# Check auto-restart processes
print_info "Checking auto-restart processes..."
WATCHMEDO_RUNNING=$(pgrep -f "watchmedo.*mcp_server.py" 2>/dev/null || true)
if [ ! -z "$WATCHMEDO_RUNNING" ]; then
    print_status "Python file watcher is active (watchmedo PID: $WATCHMEDO_RUNNING)"
else
    print_warning "Python file watcher not running (install: pip install watchdog)"
fi

if [ ! -z "$NODEMON_RUNNING" ]; then
    print_status "SocketIO file watcher is active (nodemon)"
else
    print_warning "SocketIO file watcher not running"
fi

echo ""

# Port check
print_info "Checking ports..."
check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
        print_status "Port $port is in use ($service)"
    else
        print_error "Port $port is not in use ($service not listening)"
    fi
}

check_port 8000 "MCP Server"
check_port 3001 "SocketIO Server"
check_port 1947 "Plasmo Dev Server (typical)"

echo ""

# Display URLs
print_info "Service URLs:"
echo "  • MCP Server: http://localhost:8000"
echo "  • SocketIO Controller: http://localhost:3001"
echo "  • MCP Health Check: http://localhost:8000/health"

echo ""

# Check logs
print_info "Recent log activity:"
if [ -d "logs" ]; then
    for log in logs/*.log; do
        if [ -f "$log" ]; then
            lines=$(wc -l < "$log" 2>/dev/null || echo "0")
            size=$(ls -lh "$log" | awk '{print $5}' 2>/dev/null || echo "unknown")
            echo "  • $(basename "$log"): $lines lines, $size"
        fi
    done
else
    print_warning "Logs directory not found"
fi

echo ""

# Summary
ALL_RUNNING=true

if [ -z "$MCP_RUNNING" ]; then ALL_RUNNING=false; fi
if [ -z "$SOCKETIO_RUNNING" ] && [ -z "$NODEMON_RUNNING" ]; then ALL_RUNNING=false; fi  
if [ -z "$PLASMO_RUNNING" ]; then ALL_RUNNING=false; fi

if [ "$ALL_RUNNING" = true ]; then
    print_status "🎉 All services are running!"
else
    print_error "⚠️  Some services are not running"
    echo ""
    print_info "To start all services: ./start_all_services.sh"
    print_info "To stop all services: ./stop_all_services.sh"
fi 