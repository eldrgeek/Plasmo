#!/bin/bash

# Get Chrome Extension ID (Linux version)
# =====================================

echo "🔍 Finding Plasmo Extension ID on Linux..."

# Linux Chrome preferences path
CHROME_PREFS="$HOME/.config/google-chrome/Default/Preferences"

if [ ! -f "$CHROME_PREFS" ]; then
    echo "❌ Chrome preferences not found at: $CHROME_PREFS"
    echo ""
    echo "Possible solutions:"
    echo "   1. Start Chrome at least once to create the profile"
    echo "   2. Check if Chrome is installed"
    echo "   3. Try Chromium preferences: $HOME/.config/chromium/Default/Preferences"
    exit 1
fi

echo "✅ Found Chrome preferences: $CHROME_PREFS"

# Look for Plasmo extension
POTENTIAL_ID=$(grep -o '"[a-p]*": {[^}]*"name": "My Plasmo Extension"' "$CHROME_PREFS" 2>/dev/null | cut -d'"' -f2)

if [ ! -z "$POTENTIAL_ID" ]; then
    echo "✅ Found Plasmo Extension ID: $POTENTIAL_ID"
    echo ""
    echo "📋 Extension Details:"
    echo "   ID: $POTENTIAL_ID"
    echo "   Chrome Preferences: $CHROME_PREFS"
    echo ""
    echo "🚀 To configure native messaging:"
    echo "   ./configure_extension.sh"
else
    echo "❌ Plasmo extension not found in Chrome"
    echo ""
    echo "Please ensure:"
    echo "   1. The extension is built: pnpm build"
    echo "   2. The extension is loaded in Chrome:"
    echo "      - Go to chrome://extensions/"
    echo "      - Enable Developer mode"
    echo "      - Click 'Load unpacked'"
    echo "      - Select: $(pwd)/build/chrome-mv3-dev"
    echo "   3. The extension name is 'My Plasmo Extension'"
    echo ""
    
    # Show all extensions for debugging
    echo "🔍 All extensions found:"
    grep -o '"[a-p]*": {[^}]*"name": "[^"]*"' "$CHROME_PREFS" 2>/dev/null | while read line; do
        ID=$(echo "$line" | cut -d'"' -f2)
        NAME=$(echo "$line" | sed 's/.*"name": "\([^"]*\)".*/\1/')
        echo "   $ID: $NAME"
    done
    
    exit 1
fi

# Check extensions directory
EXTENSIONS_DIR="$HOME/.config/google-chrome/Default/Extensions"
if [ -d "$EXTENSIONS_DIR/$POTENTIAL_ID" ]; then
    echo "✅ Extension files found in: $EXTENSIONS_DIR/$POTENTIAL_ID"
    
    # Show version directories
    echo "📁 Available versions:"
    ls -la "$EXTENSIONS_DIR/$POTENTIAL_ID" 2>/dev/null | grep "^d" | awk '{print "   " $NF}'
else
    echo "⚠️  Extension directory not found: $EXTENSIONS_DIR/$POTENTIAL_ID"
fi

echo ""
echo "🎯 Extension ID: $POTENTIAL_ID" 