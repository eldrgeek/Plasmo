#!/bin/bash

# Configure SocketIO Controller Extension
echo "🔧 Configuring SocketIO Cursor Controller Extension"
echo "=================================================="

# Get extension ID from user or auto-detect
EXTENSION_ID=""

# Try to auto-detect from Chrome if extension is loaded
echo "🔍 Looking for loaded Plasmo extension..."
CHROME_PREFS="$HOME/Library/Application Support/Google/Chrome/Default/Preferences"

if [ -f "$CHROME_PREFS" ]; then
    # Look for extensions with "My Plasmo Extension" name
    POTENTIAL_ID=$(grep -o '"[a-p]*": {[^}]*"name": "My Plasmo Extension"' "$CHROME_PREFS" 2>/dev/null | cut -d'"' -f2)
    if [ ! -z "$POTENTIAL_ID" ]; then
        echo "✅ Found potential extension ID: $POTENTIAL_ID"
        EXTENSION_ID=$POTENTIAL_ID
    fi
fi

# If not found, prompt user
if [ -z "$EXTENSION_ID" ]; then
    echo ""
    echo "📋 Manual Configuration Required:"
    echo "   1. Open Chrome and go to chrome://extensions/"
    echo "   2. Enable Developer mode (toggle in top right)"
    echo "   3. Click 'Load unpacked' and select: $(pwd)/build/chrome-mv3-dev"
    echo "   4. Copy the extension ID (32-character string)"
    echo ""
    read -p "🔑 Enter the extension ID: " EXTENSION_ID
fi

if [ -z "$EXTENSION_ID" ]; then
    echo "❌ Extension ID required. Exiting."
    exit 1
fi

# Validate extension ID format
if [[ ! "$EXTENSION_ID" =~ ^[a-p]{32}$ ]]; then
    echo "⚠️  Warning: Extension ID format unusual (should be 32 lowercase letters a-p)"
    read -p "Continue anyway? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔧 Configuring extension ID: $EXTENSION_ID"

# Update native messaging manifest
MANIFEST_PATH="cursor_controller_manifest.json"
if [ -f "$MANIFEST_PATH" ]; then
    # Create backup
    cp "$MANIFEST_PATH" "${MANIFEST_PATH}.backup"
    
    # Update the manifest with real extension ID
    sed "s/YOUR_EXTENSION_ID_HERE/$EXTENSION_ID/g" "$MANIFEST_PATH" > "${MANIFEST_PATH}.tmp"
    mv "${MANIFEST_PATH}.tmp" "$MANIFEST_PATH"
    echo "✅ Updated $MANIFEST_PATH"
else
    echo "❌ $MANIFEST_PATH not found"
    exit 1
fi

# Install native messaging manifest
NATIVE_MESSAGING_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
mkdir -p "$NATIVE_MESSAGING_DIR"

TARGET_MANIFEST="$NATIVE_MESSAGING_DIR/com.plasmo.cursor_controller.json"
cp "$MANIFEST_PATH" "$TARGET_MANIFEST"

if [ -f "$TARGET_MANIFEST" ]; then
    echo "✅ Installed native messaging manifest to: $TARGET_MANIFEST"
else
    echo "❌ Failed to install native messaging manifest"
    exit 1
fi

# Make cursor_controller.py executable
chmod +x cursor_controller.py
echo "✅ Made cursor_controller.py executable"

# Update the manifest path to absolute path
ABS_PATH="$(pwd)/cursor_controller.py"
sed "s|/Users/MikeWolf/Projects/Plasmo/cursor_controller.py|$ABS_PATH|g" "$TARGET_MANIFEST" > "${TARGET_MANIFEST}.tmp"
mv "${TARGET_MANIFEST}.tmp" "$TARGET_MANIFEST"
echo "✅ Updated native messaging manifest with absolute path: $ABS_PATH"

echo ""
echo "🎉 SocketIO Controller Configuration Complete!"
echo "============================================="
echo "✅ Extension ID: $EXTENSION_ID"
echo "✅ Native messaging: $TARGET_MANIFEST"
echo "✅ Controller script: $(pwd)/cursor_controller.py"
echo ""
echo "🚀 Next steps:"
echo "   1. Start the SocketIO server: node socketio_server.js"
echo "   2. Test the connection from Chrome extension"
echo "   3. Use the web interface at: http://localhost:3001" 