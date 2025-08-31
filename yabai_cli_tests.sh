#!/bin/bash

echo "🧪 Yabai CLI Test Commands"
echo "Copy and paste these commands one by one to test functionality"
echo "=" * 70

echo ""
echo "📊 1. BASIC QUERIES (These should always work)"
echo "=" * 50

echo ""
echo "# Show all spaces/desktops:"
echo "/opt/homebrew/bin/yabai -m query --spaces"

echo ""
echo "# Show current focused space:"
echo "/opt/homebrew/bin/yabai -m query --spaces --space"

echo ""
echo "# Show all windows:"
echo "/opt/homebrew/bin/yabai -m query --windows"

echo ""
echo "# Show current focused window:"
echo "/opt/homebrew/bin/yabai -m query --windows --window"

echo ""
echo "# Show current configuration:"
echo "/opt/homebrew/bin/yabai -m config layout"
echo "/opt/homebrew/bin/yabai -m config window_gap"

echo ""
echo "🖥️  2. SPACE/DESKTOP MANAGEMENT"
echo "=" * 50

echo ""
echo "# Switch to space 1 (might need scripting addition):"
echo "/opt/homebrew/bin/yabai -m space --focus 1"

echo ""
echo "# Switch to space 2:"
echo "/opt/homebrew/bin/yabai -m space --focus 2"

echo ""
echo "# Switch back to space 3:"
echo "/opt/homebrew/bin/yabai -m space --focus 3"

echo ""
echo "# Create a new space:"
echo "/opt/homebrew/bin/yabai -m space --create"

echo ""
echo "🪟 3. WINDOW FOCUS COMMANDS"
echo "=" * 50

echo ""
echo "# Focus next window:"
echo "/opt/homebrew/bin/yabai -m window --focus next"

echo ""
echo "# Focus previous window:"
echo "/opt/homebrew/bin/yabai -m window --focus prev"

echo ""
echo "# Focus window to the left:"
echo "/opt/homebrew/bin/yabai -m window --focus west"

echo ""
echo "# Focus window to the right:"
echo "/opt/homebrew/bin/yabai -m window --focus east"

echo ""
echo "# Focus window above:"
echo "/opt/homebrew/bin/yabai -m window --focus north"

echo ""
echo "# Focus window below:"
echo "/opt/homebrew/bin/yabai -m window --focus south"

echo ""
echo "🔄 4. WINDOW MOVEMENT COMMANDS"
echo "=" * 50

echo ""
echo "# Swap current window with next:"
echo "/opt/homebrew/bin/yabai -m window --swap next"

echo ""
echo "# Swap current window with previous:"
echo "/opt/homebrew/bin/yabai -m window --swap prev"

echo ""
echo "# Move window left:"
echo "/opt/homebrew/bin/yabai -m window --swap west"

echo ""
echo "# Move window right:"
echo "/opt/homebrew/bin/yabai -m window --swap east"

echo ""
echo "🎛️  5. WINDOW STATE COMMANDS"
echo "=" * 50

echo ""
echo "# Toggle current window floating:"
echo "/opt/homebrew/bin/yabai -m window --toggle float"

echo ""
echo "# Toggle current window fullscreen:"
echo "/opt/homebrew/bin/yabai -m window --toggle zoom-fullscreen"

echo ""
echo "# Toggle parent zoom (expand to fill half):"
echo "/opt/homebrew/bin/yabai -m window --toggle zoom-parent"

echo ""
echo "# Minimize current window:"
echo "/opt/homebrew/bin/yabai -m window --minimize"

echo ""
echo "🔧 6. SPACE LAYOUT COMMANDS"
echo "=" * 50

echo ""
echo "# Set current space to BSP (tiling) layout:"
echo "/opt/homebrew/bin/yabai -m space --layout bsp"

echo ""
echo "# Set current space to stack layout:"
echo "/opt/homebrew/bin/yabai -m space --layout stack"

echo ""
echo "# Set current space to float layout:"
echo "/opt/homebrew/bin/yabai -m space --layout float"

echo ""
echo "# Balance all windows (equal sizes):"
echo "/opt/homebrew/bin/yabai -m space --balance"

echo ""
echo "# Rotate windows 90 degrees:"
echo "/opt/homebrew/bin/yabai -m space --rotate 90"

echo ""
echo "# Mirror windows on Y axis:"
echo "/opt/homebrew/bin/yabai -m space --mirror y-axis"

echo ""
echo "🏠 7. SEND WINDOWS TO OTHER SPACES"
echo "=" * 50

echo ""
echo "# Send current window to space 1:"
echo "/opt/homebrew/bin/yabai -m window --space 1"

echo ""
echo "# Send current window to space 2:"
echo "/opt/homebrew/bin/yabai -m window --space 2"

echo ""
echo "🔧 8. CONFIGURATION CHANGES"
echo "=" * 50

echo ""
echo "# Change window gap to 15px:"
echo "/opt/homebrew/bin/yabai -m config window_gap 15"

echo ""
echo "# Change window gap back to 10px:"
echo "/opt/homebrew/bin/yabai -m config window_gap 10"

echo ""
echo "# Turn window borders on:"
echo "/opt/homebrew/bin/yabai -m config window_border on"

echo ""
echo "# Turn window borders off:"
echo "/opt/homebrew/bin/yabai -m config window_border off"

echo ""
echo "🔍 9. DEBUGGING COMMANDS"
echo "=" * 50

echo ""
echo "# Check if scripting addition is loaded:"
echo "/opt/homebrew/bin/yabai -m query --windows | head -5"

echo ""
echo "# Show Yabai version:"
echo "/opt/homebrew/bin/yabai --version"

echo ""
echo "# Test if Yabai service is running:"
echo "ps aux | grep yabai | grep -v grep"

echo ""
echo "# Check Yabai logs:"
echo "tail -20 /tmp/yabai_\$USER.out.log"

echo ""
echo "🎯 10. QUICK TEST SEQUENCE"
echo "=" * 50
echo "# Run these in order to test core functionality:"
echo ""
echo "echo '1. Query current space:'"
echo "/opt/homebrew/bin/yabai -m query --spaces --space"
echo ""
echo "echo '2. Toggle window floating:'"
echo "/opt/homebrew/bin/yabai -m window --toggle float"
echo ""
echo "echo '3. Toggle back:'"
echo "/opt/homebrew/bin/yabai -m window --toggle float"
echo ""
echo "echo '4. Try to balance windows:'"
echo "/opt/homebrew/bin/yabai -m space --balance"
echo ""
echo "echo '5. Try to focus next window:'"
echo "/opt/homebrew/bin/yabai -m window --focus next"

echo ""
echo "💡 USAGE INSTRUCTIONS:"
echo "=" * 50
echo "1. Open multiple application windows first"
echo "2. Copy and paste commands one by one"
echo "3. Watch for error messages vs success"
echo "4. Commands that work = those functions are available"
echo "5. Commands that fail = need scripting addition or have other issues"
echo ""
echo "📊 After testing, run our mapper to see changes:"
echo "cd /Users/MikeWolf/Projects/Plasmo && python3 complete_mapper.py"
