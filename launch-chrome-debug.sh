#!/bin/bash

echo "🟣 Launching Chrome with Plasmo Extension in Debug Mode..."
echo "📦 This will load the built Plasmo extension with debugging enabled"

# Close existing Chrome (gracefully)
echo "🚪 Closing existing Chrome instances..."
osascript -e 'quit app "Google Chrome"' 2>/dev/null || true
sleep 2

# Kill any remaining Chrome processes
pkill -f "Google Chrome" 2>/dev/null || true
pkill -f "chrome" 2>/dev/null || true
sleep 2

# Build the extension first if needed
if [ ! -d "./build/chrome-mv3-dev" ]; then
    echo "🔨 Building Plasmo extension..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build extension"
        exit 1
    fi
fi

# Find the Plasmo extension path
EXTENSION_PATH="./build/chrome-mv3-dev"
if [ ! -d "$EXTENSION_PATH" ]; then
    echo "❌ Plasmo extension not found at $EXTENSION_PATH"
    echo "💡 Run 'npm run build' first"
    exit 1
fi

echo "📁 Plasmo extension path: $(realpath $EXTENSION_PATH)"

# Create a clean profile directory for debugging
DEBUG_PROFILE="./chrome-debug-profile"
rm -rf "$DEBUG_PROFILE" 2>/dev/null || true
mkdir -p "$DEBUG_PROFILE"

echo "🆔 Using clean debug profile: $(realpath $DEBUG_PROFILE)"

# Start Chrome with debugging and Plasmo extension
echo "🚀 Starting Chrome with Plasmo extension and debugging..."
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --remote-debugging-address=127.0.0.1 \
    --remote-allow-origins=http://localhost:9222,http://127.0.0.1:9222 \
    --load-extension="$(realpath $EXTENSION_PATH)" \
    --disable-extensions-except="$(realpath $EXTENSION_PATH)" \
    --user-data-dir="$(realpath $DEBUG_PROFILE)" \
    --disable-infobars \
    --disable-extensions-file-access-check \
    --disable-popup-blocking \
    --disable-default-apps \
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    --disable-dev-shm-usage \
    --no-first-run \
    --no-default-browser-check \
    --window-size=1400,900 \
    --new-window \
    "chrome://extensions/" \
    > /dev/null 2>&1 &

echo "⏳ Waiting for Chrome to initialize..."
sleep 6

# Get the Chrome PID
CHROME_PID=$(pgrep -f "remote-debugging-port=9222" | head -1)

if [ -z "$CHROME_PID" ]; then
    echo "❌ Chrome failed to start with debugging enabled"
    exit 1
fi

echo "✅ Chrome started with Plasmo extension (PID: $CHROME_PID)"

# Test debugging port
echo "🔍 Testing debugging port..."
sleep 2

if curl -s --connect-timeout 5 http://localhost:9222/json > /dev/null; then
    echo "✅ Debugging port is accessible!"
    echo "🌐 DevTools endpoint: http://localhost:9222"
    echo "🔧 Chrome DevTools: chrome://inspect"
else
    echo "⚠️ Debugging port not ready, trying again..."
    sleep 3
    if curl -s --connect-timeout 5 http://localhost:9222/json > /dev/null; then
        echo "✅ Debugging port is now accessible!"
    else
        echo "❌ Debugging port not accessible"
    fi
fi

echo ""
echo "🟣 Plasmo Extension Debugging Ready!"
echo "📋 Extension ID: Check chrome://extensions/"
echo "🔍 CDP endpoint: http://localhost:9222"
echo "🛠️ Chrome opened with extensions page for easy debugging"
echo ""
echo "💡 Useful commands:"
echo "   • chrome://extensions/ - Manage extensions"
echo "   • chrome://inspect/ - DevTools for extensions"
echo "   • chrome://extension-internals/ - Extension internals"
echo ""
echo "🏠 Working from Plasmo project directory: $(pwd)" 