#!/bin/bash

# 🎯 Quick Setup Script for Instant AI Capture System
# Beautiful, modern capture system with global hotkey support

echo "🚀 Setting up Beautiful Instant AI Capture System..."
echo "================================================="

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install pynput requests

# Make the script executable
chmod +x instant_capture_beautiful.py

# Test Python version
python3_version=$(python3 --version)
echo "✅ Python: $python3_version"

# Create GTD directory structure
mkdir -p gtd
echo "✅ GTD directory structure ready"

echo ""
echo "🎯 READY TO LAUNCH!"
echo "================================================="
echo ""
echo "🚀 TO START YOUR AI CAPTURE SYSTEM:"
echo "   python3 instant_capture_beautiful.py"
echo ""
echo "✨ BEAUTIFUL FEATURES:"
echo "   • Modern dark theme with glassmorphism effects"
echo "   • Global hotkey Cmd+Shift+T works anywhere"
echo "   • Smart AI routing to correct GTD files"
echo "   • Context tags for ADD-friendly organization"
echo "   • Native Mac notifications"
echo "   • Always-on-top popup that interrupts everything"
echo ""
echo "🧠 ADD-OPTIMIZED:"
echo "   • Single-focus capture (no overwhelming lists)"
echo "   • Context-based organization (@Computer, @Mac, @Energy_High, @Energy_Low)"
echo "   • Smart categorization (Next Actions, Projects, Someday/Maybe, Waiting For)"
echo "   • Quick 5-second capture workflow"
echo ""
echo "📁 GTD FILES WILL BE CREATED:"
echo "   ./gtd/inbox.md          (Brain dump catchall)"
echo "   ./gtd/next_actions.md   (Actionable items by context)"
echo "   ./gtd/projects.md       (Multi-step outcomes)"
echo "   ./gtd/someday_maybe.md  (Future possibilities)"
echo "   ./gtd/waiting_for.md    (Blocked on others)"
echo ""
echo "🎯 Your Personal AI Sidekick is ready to capture everything!"
echo "================================================="
