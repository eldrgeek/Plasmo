#!/bin/bash

# Start All Development Services
# Handles initial setup, dependency installation, and service startup with real-time monitoring

echo "🚀 Starting All Development Services"
echo "====================================="

# Function to check if we're in a virtual environment
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        return 0  # In venv
    else
        return 1  # Not in venv
    fi
}

# Function to setup Python virtual environment and dependencies
setup_python_env() {
    echo "🐍 Setting up Python environment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create virtual environment"
            echo "💡 Make sure python3 is installed: brew install python3"
            exit 1
        fi
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment if not already active
    if ! check_venv; then
        echo "🔌 Activating virtual environment..."
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "✅ Already in virtual environment"
    fi
    
    # Check if requirements are installed
    if [ -f "requirements.txt" ]; then
        echo "📋 Checking Python dependencies..."
        
        # Quick check - if key packages are available, skip pip install
        if python3 -c "import fastmcp, websockets, aiohttp, pychrome, requests" 2>/dev/null; then
            echo "✅ Python dependencies already installed"
        else
            echo "📦 Installing Python dependencies..."
            pip install -r requirements.txt
            if [ $? -ne 0 ]; then
                echo "❌ Failed to install Python dependencies"
                exit 1
            fi
            echo "✅ Python dependencies installed"
        fi
    else
        echo "⚠️  requirements.txt not found, skipping Python dependencies"
    fi
}

# Function to setup Node/TypeScript dependencies
setup_node_env() {
    echo "📦 Setting up Node.js environment..."
    
    # Check if pnpm is installed
    if ! command -v pnpm &> /dev/null; then
        echo "❌ pnpm not found"
        echo "💡 Install pnpm: npm install -g pnpm"
        exit 1
    fi
    
    # Check if node_modules exists and has content
    if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules 2>/dev/null)" ]; then
        echo "📦 Installing Node.js dependencies..."
        pnpm install
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install Node.js dependencies"
            exit 1
        fi
        echo "✅ Node.js dependencies installed"
    else
        echo "✅ Node.js dependencies already installed"
    fi
    
    # Check if plasmo is available
    if [ -f "node_modules/.bin/plasmo" ] || command -v plasmo &> /dev/null; then
        echo "✅ Plasmo framework ready"
    else
        echo "⚠️  Plasmo not found in node_modules, but continuing..."
    fi
}

# Function to verify required files exist
verify_requirements() {
    echo "🔍 Verifying project requirements..."
    
    local missing_files=()
    
    # Check for essential files
    [ ! -f "package.json" ] && missing_files+=("package.json")
    [ ! -f "mcp_server.py" ] && missing_files+=("mcp_server.py")
    [ ! -f "start_mcp_auto_restart.sh" ] && missing_files+=("start_mcp_auto_restart.sh")
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        echo "❌ Missing required files:"
        printf '   • %s\n' "${missing_files[@]}"
        echo "💡 Make sure you're in the correct Plasmo project directory"
        exit 1
    fi
    
    echo "✅ All required files present"
}

# Function to display setup summary
setup_summary() {
    echo ""
    echo "🎯 Environment Setup Complete!"
    echo "=============================="
    echo "✅ Python virtual environment ready"
    echo "✅ Python dependencies installed"
    echo "✅ Node.js dependencies installed"
    echo "✅ Project files verified"
    echo ""
    echo "🚀 Starting development services..."
    echo ""
}

# Main setup function
initial_setup() {
    echo "🔧 Initial Environment Setup"
    echo "=============================="
    
    verify_requirements
    setup_python_env
    setup_node_env
    setup_summary
}

# Run initial setup
initial_setup

# Create logs directory
mkdir -p logs

# Check for existing instances and clean up
echo "🧹 Checking for existing service instances..."
if pgrep -f "mcp_server.py" > /dev/null || pgrep -f "start_mcp_auto_restart" > /dev/null || pgrep -f "plasmo.*dev" > /dev/null || pgrep -f "socketio_server.js" > /dev/null; then
    echo "⚠️  Found existing instances, cleaning up..."
    pkill -f "start_mcp_auto_restart" 2>/dev/null || true
    pkill -f "mcp_server.py" 2>/dev/null || true
    pkill -f "plasmo.*dev" 2>/dev/null || true
    pkill -f "socketio_server.js" 2>/dev/null || true
    pkill -f "continuous_test_runner" 2>/dev/null || true
    sleep 3
    echo "✅ Cleanup complete"
fi

# Function to start MCP server with auto-restart
start_mcp_server() {
    echo "🐍 Starting MCP Server with auto-restart..."
    
    if [ ! -f "start_mcp_auto_restart.sh" ]; then
        echo "❌ Error: start_mcp_auto_restart.sh not found!"
        return 1
    fi
    
    chmod +x start_mcp_auto_restart.sh
    
    # Ensure we're in the virtual environment for the MCP server
    if ! check_venv; then
        source venv/bin/activate
    fi
    
    nohup ./start_mcp_auto_restart.sh > logs/mcp_server.log 2>&1 &
    MCP_PID=$!
    echo "✅ MCP Server started with auto-restart (PID: $MCP_PID)"
    return 0
}

# Function to start Plasmo dev server
start_plasmo_dev() {
    echo "🎯 Starting Plasmo Dev Server (with built-in auto-reload)..."
    
    if [ ! -f "package.json" ]; then
        echo "❌ Error: package.json not found!"
        return 1
    fi
    
    nohup pnpm dev > logs/plasmo_dev.log 2>&1 &
    PLASMO_PID=$!
    echo "✅ Plasmo Dev Server started (PID: $PLASMO_PID)"
    return 0
}

# Function to start SocketIO server with auto-restart
start_socketio_server() {
    echo "🌐 Starting SocketIO Server with auto-restart..."
    
    if [ ! -f "socketio_server.js" ]; then
        echo "⚠️  socketio_server.js not found, skipping..."
        return 0
    fi
    
    # Check if nodemon is available
    if ! command -v nodemon &> /dev/null; then
        echo "⚠️  nodemon not found, installing..."
        pnpm add -D nodemon
    fi
    
    nohup nodemon --watch socketio_server.js --watch cursor_ai_injector.py \
        --exec "node socketio_server.js" > logs/socketio_server.log 2>&1 &
    SOCKETIO_PID=$!
    echo "✅ SocketIO Server started with auto-restart (PID: $SOCKETIO_PID)"
    return 0
}

# Function to start continuous test runner (optional)
start_test_runner() {
    echo "🧪 Starting Continuous Test Runner..."
    
    if [ ! -f "continuous_test_runner.py" ]; then
        echo "⚠️  continuous_test_runner.py not found, skipping..."
        return 0
    fi
    
    # Ensure we're in the virtual environment for the test runner
    if ! check_venv; then
        source venv/bin/activate
    fi
    
    nohup python3 continuous_test_runner.py > logs/continuous_testing.log 2>&1 &
    TEST_RUNNER_PID=$!
    echo "✅ Continuous Test Runner started (PID: $TEST_RUNNER_PID)"
    return 0
}

# Function to monitor and display service activity
monitor_services() {
    echo ""
    echo "👁️  Starting real-time service monitoring..."
    echo "   Press Ctrl+C to stop monitoring and all services"
    echo ""
    
    # Function to display timestamped logs with service prefix
    tail_with_prefix() {
        local logfile="$1"
        local prefix="$2"
        local color="$3"
        
        if [ -f "$logfile" ]; then
            tail -f "$logfile" 2>/dev/null | while read line; do
                echo -e "${color}[$(date '+%H:%M:%S')] $prefix:${NC} $line"
            done &
        fi
    }
    
    # Color codes
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    NC='\033[0m' # No Color
    
    # Start monitoring each service log
    tail_with_prefix "logs/mcp_server.log" "🐍 MCP" "$GREEN"
    tail_with_prefix "logs/plasmo_dev.log" "🎯 PLASMO" "$BLUE"
    tail_with_prefix "logs/socketio_server.log" "🌐 SOCKET" "$YELLOW"
    tail_with_prefix "logs/continuous_testing.log" "🧪 TEST" "$PURPLE"
    
    # Monitor for service restarts
    while true; do
        sleep 5
        
        # Check for new PID changes (indicating restarts)
        if [ -f ".service_pids" ]; then
            source .service_pids
            
            # Check if services are still running, show restart notifications
            current_mcp=$(pgrep -f "mcp_server.py --port" | head -1)
            current_plasmo=$(pgrep -f "plasmo.*dev" | head -1)
            current_socketio=$(pgrep -f "socketio_server.js" | head -1)
            current_test=$(pgrep -f "continuous_test_runner" | head -1)
            
            if [ ! -z "$current_mcp" ] && [ "$current_mcp" != "$MCP_PID" ]; then
                echo -e "${GREEN}[$(date '+%H:%M:%S')] 🔄 MCP SERVER RESTARTED${NC} (New PID: $current_mcp)"
                echo "MCP_PID=$current_mcp" > .service_pids.tmp
                echo "PLASMO_PID=$PLASMO_PID" >> .service_pids.tmp
                echo "SOCKETIO_PID=$SOCKETIO_PID" >> .service_pids.tmp
                echo "TEST_RUNNER_PID=$TEST_RUNNER_PID" >> .service_pids.tmp
                mv .service_pids.tmp .service_pids
                MCP_PID=$current_mcp
            fi
        fi
    done
}

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down all services..."
    
    # Kill monitoring processes
    jobs -p | xargs -r kill 2>/dev/null
    
    # Kill all services
    pkill -f "start_mcp_auto_restart" 2>/dev/null || true
    pkill -f "mcp_server.py" 2>/dev/null || true
    pkill -f "plasmo.*dev" 2>/dev/null || true
    pkill -f "socketio_server.js" 2>/dev/null || true
    pkill -f "continuous_test_runner" 2>/dev/null || true
    
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start all services
echo ""
echo "🚀 Starting all services..."

start_mcp_server
sleep 3

start_plasmo_dev
sleep 2

start_socketio_server
sleep 2

start_test_runner
sleep 2

# Save PIDs for potential cleanup
echo "MCP_PID=$MCP_PID" > .service_pids
echo "PLASMO_PID=$PLASMO_PID" >> .service_pids
echo "SOCKETIO_PID=$SOCKETIO_PID" >> .service_pids
echo "TEST_RUNNER_PID=$TEST_RUNNER_PID" >> .service_pids

echo ""
echo "🎉 All Services Started!"
echo "========================"
echo "📊 Service Status:"
echo "  • MCP Server (PID: $MCP_PID) - http://localhost:8000/mcp"
echo "  • Plasmo Dev Server (PID: $PLASMO_PID) - Built-in auto-reload"
echo "  • SocketIO Server (PID: $SOCKETIO_PID) - http://localhost:3001"
echo "  • Test Runner (PID: $TEST_RUNNER_PID) - Auto-testing"
echo ""
echo "📁 Log Files:"
echo "  • MCP Server: logs/mcp_server.log"
echo "  • Plasmo Dev: logs/plasmo_dev.log"
echo "  • SocketIO Server: logs/socketio_server.log"
echo "  • Continuous Testing: logs/continuous_testing.log"
echo ""
echo "🔧 Auto-Restart Enabled For:"
echo "  • MCP Server: *.py files (via start_mcp_auto_restart.sh)"
echo "  • Plasmo Dev: Built-in hot reload for extension files"
echo "  • SocketIO Server: socketio_server.js, cursor_ai_injector.py (via nodemon)"
echo "  • Test Runner: *.ts, *.tsx, *.js, *.jsx, *.html, *.css, *.py files"

# Start monitoring (this will run until Ctrl+C)
monitor_services 