#!/bin/bash
echo "🔄 Restarting SKHD after permission changes..."
/opt/homebrew/bin/skhd --restart-service
sleep 2
echo "✅ SKHD restarted"
echo ""
echo "🧪 Test these hotkeys now:"
echo "   • Option ⌥ + 1  →  Switch to desktop 1"
echo "   • Option ⌥ + 2  →  Switch to desktop 2"
echo "   • Option ⌥ + F  →  Toggle fullscreen"
echo ""
echo "If hotkeys still don't work:"
echo "   • Check System Settings → Keyboard → Shortcuts for conflicts"
echo "   • Try Option ⌥ + F first (less likely to conflict)"
echo "   • Ensure you added /opt/homebrew/bin/skhd to Input Monitoring"
