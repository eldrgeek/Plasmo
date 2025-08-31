#!/bin/bash

echo "🔍 Debugging Yabai Float Toggle Issue"
echo "=" * 50

echo ""
echo "1️⃣ Check current window state BEFORE toggle:"
/opt/homebrew/bin/yabai -m query --windows --window | grep -E '"is-floating"|"app"|"title"'

echo ""
echo "2️⃣ Toggle to floating:"
/opt/homebrew/bin/yabai -m window --toggle float

echo ""
echo "3️⃣ Check window state AFTER first toggle:"
/opt/homebrew/bin/yabai -m query --windows --window | grep -E '"is-floating"|"app"|"title"'

echo ""
echo "4️⃣ Toggle back to tiled:"
/opt/homebrew/bin/yabai -m window --toggle float

echo ""
echo "5️⃣ Check window state AFTER second toggle:"
/opt/homebrew/bin/yabai -m query --windows --window | grep -E '"is-floating"|"app"|"title"'

echo ""
echo "6️⃣ Space layout info:"
/opt/homebrew/bin/yabai -m query --spaces --space | grep -E '"type"|"index"'

echo ""
echo "💡 Analysis:"
echo "• is-floating should change from false → true → false"
echo "• If it gets stuck at true, there's a float toggle bug"
echo "• If app shows 'Unknown', there might be a focus issue"
