#!/bin/bash

# Launch Chrome with debugging enabled for MCP server
# This script launches Chrome with remote debugging port 9222

echo "🚀 Launching Chrome with Debug Protocol enabled..."
echo "Debug port: 9222"
echo "Profile directory: ./chrome-debug-profile"

# Kill any existing Chrome instances using the debug profile
pkill -f "chrome-debug-profile" 2>/dev/null

# Create profile directory if it doesn't exist
mkdir -p chrome-debug-profile

# Try different Chrome executable paths based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CHROME_PATH=$(which google-chrome || which chrome || which chromium || which chromium-browser)
else
    # Windows (Git Bash/WSL)
    CHROME_PATH="chrome.exe"
fi

# Chrome launch arguments
CHROME_ARGS=(
    --remote-debugging-port=9222
    --remote-allow-origins=*
    --no-first-run
    --no-default-browser-check
    --disable-web-security
    --disable-features=VizDisplayCompositor
    --user-data-dir=./chrome-debug-profile
    --new-window
)

# Launch Chrome
if [ -x "$CHROME_PATH" ]; then
    echo "Using Chrome at: $CHROME_PATH"
    "$CHROME_PATH" "${CHROME_ARGS[@]}" > /dev/null 2>&1 &
    
    echo "✅ Chrome launched with debugging enabled!"
    echo "🌐 Debug URL: http://localhost:9222"
    echo "📋 To connect from MCP server, use: connect_to_chrome()"
    echo ""
    echo "Chrome will open with a new window. You can now:"
    echo "1. Navigate to your web application"
    echo "2. Use the MCP server tools to monitor console logs"
    echo "3. Debug JavaScript execution"
    echo ""
    echo "To view Chrome's debug interface, visit: http://localhost:9222"
else
    echo "❌ Chrome executable not found!"
    echo "Please ensure Chrome is installed and accessible."
    echo "Tried: $CHROME_PATH"
fi 