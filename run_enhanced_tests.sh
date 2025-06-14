#!/bin/bash

# Enhanced Test Runner Launcher
# Runs WebRTC and CDP tests with smart file watching

echo "🚀 Starting Enhanced Continuous Test Runner"
echo "   📊 Features: CDP tests, WebRTC tests, dual endpoints, smart file watching"
echo ""

# Ensure logs directory exists
mkdir -p logs

# Check if Python virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Python virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider activating venv."
    if [[ -d "venv" ]]; then
        echo "   Run: source venv/bin/activate"
    fi
fi

# Check dependencies
echo "🔍 Checking dependencies..."

MISSING_DEPS=()

# Check Python packages
python -c "import socketio" 2>/dev/null || MISSING_DEPS+=("python-socketio")
python -c "import aiohttp" 2>/dev/null || MISSING_DEPS+=("aiohttp")
python -c "import websockets" 2>/dev/null || MISSING_DEPS+=("websockets")
python -c "import watchdog" 2>/dev/null || MISSING_DEPS+=("watchdog")

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo "❌ Missing dependencies: ${MISSING_DEPS[*]}"
    echo "   Install with: pip install ${MISSING_DEPS[*]}"
    exit 1
fi

echo "✅ All dependencies found"

# Check if services are running
echo "🔍 Checking service status..."

# Check Socket.IO server
if curl -s "http://localhost:3001/health" > /dev/null 2>&1; then
    echo "✅ Socket.IO server running on port 3001"
else
    echo "⚠️  Socket.IO server not running on port 3001"
    echo "   Start with: python socketio_server_python.py"
fi

# Check Chrome Debug Protocol
if curl -s "http://localhost:9222/json" > /dev/null 2>&1; then
    echo "✅ Chrome Debug Protocol available on port 9222"
else
    echo "⚠️  Chrome Debug Protocol not available on port 9222"
    echo "   Start Chrome with: --remote-debugging-port=9222 --remote-allow-origins=*"
fi

# Check tunnel server (optional)
if curl -s "https://monad-socketio.loca.lt/health" > /dev/null 2>&1; then
    echo "✅ Tunnel server accessible"
else
    echo "⚠️  Tunnel server not accessible (optional)"
fi

echo ""
echo "🧪 Starting enhanced test runner..."
echo "   Health endpoint: http://localhost:8083/health"
echo "   Press Ctrl+C to stop"
echo ""

# Run the enhanced test runner
exec python continuous_test_runner_enhanced.py 