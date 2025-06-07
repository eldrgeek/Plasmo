#!/bin/bash

# Script to find the Plasmo extension ID in Chrome
echo "🔍 Looking for Plasmo Chrome extension ID..."

# Check Chrome preferences for extensions
CHROME_PREFS="$HOME/Library/Application Support/Google/Chrome/Default/Preferences"
if [ -f "$CHROME_PREFS" ]; then
    echo "📁 Checking Chrome preferences..."
    
    # Look for extensions with "plasmo" in the name or manifest
    grep -o '"[a-z]*": {[^}]*"name"[^}]*[Pp]lasmo[^}]*}' "$CHROME_PREFS" 2>/dev/null | head -3
    
    echo ""
    echo "🔧 Alternative: Check chrome://extensions/ for the extension ID"
    echo "   The ID is a 32-character string like: abcdefghijklmnopqrstuvwxyz123456"
fi

# Also check the extension install location
EXTENSIONS_DIR="$HOME/Library/Application Support/Google/Chrome/Default/Extensions"
if [ -d "$EXTENSIONS_DIR" ]; then
    echo ""
    echo "📂 Chrome extensions directory:"
    ls -la "$EXTENSIONS_DIR" | grep -E "^d" | tail -5
fi

echo ""
echo "💡 To get the extension ID:"
echo "   1. Open Chrome and go to chrome://extensions/"
echo "   2. Enable Developer mode"
echo "   3. Find 'My Plasmo Extension' and copy the ID"
echo "   4. Or load the extension from: $(pwd)/build/chrome-mv3-dev" 