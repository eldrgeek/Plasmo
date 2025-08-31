#!/bin/bash

# 🚀 Build Native Mac App for Instant AI Capture

echo "🎯 Building Native Mac App for Instant AI Capture..."

cd capture_ui

# Check if Xcode is available
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode not found. Installing Xcode Command Line Tools..."
    xcode-select --install
    echo "Please run this script again after Xcode installation completes."
    exit 1
fi

echo "📦 Building Swift package..."
swift build -c release

echo "🏗️ Creating Mac app bundle..."
mkdir -p InstantCapture.app/Contents/MacOS
mkdir -p InstantCapture.app/Contents/Resources

# Create Info.plist
cat > InstantCapture.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>InstantCapture</string>
    <key>CFBundleIdentifier</key>
    <string>com.mikewolf.instantcapture</string>
    <key>CFBundleName</key>
    <string>Instant AI Capture</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>This app uses microphone for voice task capture.</string>
</dict>
</plist>
EOF

# Copy executable
cp .build/release/InstantCapture InstantCapture.app/Contents/MacOS/

echo "✅ Mac app created: InstantCapture.app"
echo ""
echo "🚀 TO RUN:"
echo "   Double-click InstantCapture.app"
echo "   OR: open InstantCapture.app"
echo ""
echo "🎯 FEATURES:"
echo "   • Always on top popup"
echo "   • Global hotkey Cmd+Shift+T"
echo "   • Native Mac look & feel"
echo "   • Voice recognition"
echo "   • Auto-saves to GTD files"
echo ""
echo "🎨 Beautiful native Mac app with glassmorphism effects!"
