#!/bin/bash

# 🚀 Setup script for Instant AI Capture System

echo "🎯 Setting up Instant AI Capture for Mike Wolf..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install speechrecognition pynput pyaudio requests

# Make the script executable
chmod +x instant_ai_capture.py

# Create GTD directory structure
mkdir -p gtd

echo "✅ Setup complete!"
echo ""
echo "🚀 TO START THE CAPTURE SYSTEM:"
echo "   python3 instant_ai_capture.py"
echo ""
echo "🎯 USAGE:"
echo "   1. Run the script above"
echo "   2. Press Cmd+Shift+T anywhere on your Mac"
echo "   3. Type or speak your task"
echo "   4. AI automatically routes it to the right GTD file"
echo ""
echo "📁 GTD FILES WILL BE CREATED IN:"
echo "   ./gtd/inbox.md"
echo "   ./gtd/next_actions.md" 
echo "   ./gtd/projects.md"
echo "   ./gtd/someday_maybe.md"
echo "   ./gtd/waiting_for.md"
echo ""
echo "🤖 Your AI sidekick will intelligently categorize everything!"
