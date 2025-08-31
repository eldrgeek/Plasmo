#!/bin/bash

echo "🔍 Practical Examples: Yabai vs OSAScript"
echo "=" * 60

echo ""
echo "1️⃣ WINDOW POSITION - Only Yabai Can Do This:"
echo "=" * 50
echo "# Get exact window coordinates:"
echo "/opt/homebrew/bin/yabai -m query --windows --window | grep frame"
echo ""
echo "# AppleScript equivalent (doesn't work well):"
echo "# osascript -e 'tell app \"System Events\" to get position of window 1 of process \"Claude\"'"

echo ""
echo "2️⃣ ALL RUNNING APPS - Only OSAScript Can Do This:"
echo "=" * 50
echo "# AppleScript can see background processes:"
echo "osascript -e 'tell app \"System Events\" to get name of every process whose background only is false'"
echo ""
echo "# Yabai equivalent (limited to apps with windows):"
echo "/opt/homebrew/bin/yabai -m query --windows | grep '\"app\"' | sort -u"

echo ""
echo "3️⃣ DESKTOP/SPACE ASSIGNMENT - Only Yabai:"
echo "=" * 50
echo "# Which desktop is each window on:"
echo "/opt/homebrew/bin/yabai -m query --windows | grep -E '\"app\"|\"space\"'"
echo ""
echo "# AppleScript cannot determine this"

echo ""
echo "4️⃣ SYSTEM INTEGRATION - Only OSAScript:"
echo "=" * 50
echo "# Launch an application:"
echo "osascript -e 'tell application \"Calculator\" to activate'"
echo ""
echo "# Check if app is in Dock:"
echo "osascript -e 'tell app \"System Events\" to get name of dock items' | grep Calculator"
echo ""
echo "# Yabai cannot launch apps or check Dock"

echo ""
echo "5️⃣ WINDOW STATES - Only Yabai:"
echo "=" * 50
echo "# Check if window is floating or tiled:"
echo "/opt/homebrew/bin/yabai -m query --windows --window | grep is-floating"
echo ""
echo "# Toggle window between floating and tiled:"
echo "/opt/homebrew/bin/yabai -m window --toggle float"
echo ""
echo "# AppleScript cannot determine tiling states"

echo ""
echo "6️⃣ PROCESS INFORMATION - Only OSAScript:"
echo "=" * 50
echo "# Get detailed process info:"
echo "osascript -e 'tell app \"System Events\" to get {name, unix id, visible, frontmost} of every process whose name is \"Claude\"'"
echo ""
echo "# Yabai shows PID but not process details:"
echo "/opt/homebrew/bin/yabai -m query --windows | grep -A5 -B5 Claude | grep pid"

echo ""
echo "💡 WHEN TO USE EACH:"
echo "=" * 50
echo "Use YABAI for:"
echo "  • Moving/resizing windows programmatically"
echo "  • Checking window layout states"
echo "  • Managing multi-desktop workflows"
echo "  • Building tiling window manager scripts"
echo ""
echo "Use OSASCRIPT for:"
echo "  • Launching applications"
echo "  • Getting system-wide app lists"
echo "  • Menu automation and UI interaction"
echo "  • Process monitoring and system integration"
echo ""
echo "Use BOTH together for:"
echo "  • Complete application management systems"
echo "  • Advanced workspace automation"
echo "  • Comprehensive system monitoring"
