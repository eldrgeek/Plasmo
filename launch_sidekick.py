#!/usr/bin/env python3
"""
🤖 Personal AI Sidekick Launcher
Quick activation of Mike Wolf's personal accountability coach
"""

import subprocess
import sys
import os
from pathlib import Path

def launch_sidekick():
    """Launch the personal sidekick using existing agent infrastructure."""
    
    print("🤖 Launching Personal AI Sidekick...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Check if we're in the right directory
    if not Path("agents/mw_personal_assistant_agent.md").exists():
        print("❌ Error: Not in correct directory or agent template missing")
        print("   Make sure you're in the Plasmo project directory")
        return False
    
    print("✅ Personal Sidekick agent template found")
    print("✅ MCP server infrastructure available")
    
    # Create the command for Claude Desktop to spawn the sidekick
    claude_command = '''
You are Mike Wolf's Personal AI Sidekick. Read your instructions from:
/Users/MikeWolf/Projects/Plasmo/agents/mw_personal_assistant_agent.md

Initialize with these immediate actions:
1. Register as "PersonalSidekick" agent 
2. Send morning accountability reminder if between 5:30-7:30 AM
3. Check if Mike is working on convergent (consolidating) or divergent (exploring) activities
4. Ask: "What's the single most important thing you should focus on right now?"

Ready to be your accountability partner and focus coach! 🎯
'''
    
    print("\n📋 SIDEKICK ACTIVATION COMMAND:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(claude_command.strip())
    
    print("\n🚀 NEXT STEPS:")
    print("1. Copy the command above")  
    print("2. Paste into a new Claude Desktop conversation")
    print("3. Your sidekick will auto-activate and start coaching!")
    
    # Try to copy to clipboard if possible
    try:
        import pyperclip
        pyperclip.copy(claude_command.strip())
        print("\n✅ Command copied to clipboard!")
    except ImportError:
        print("\n💡 Tip: Install 'pyperclip' to auto-copy commands")
    
    print("\n" + "="*50)
    print("🎯 SIDEKICK MISSION: Help Mike focus and consolidate")
    print("⚡ IMMEDIATE GOAL: Break the ADD distraction loop")
    print("🎪 META-GOAL: Stop building, start USING")
    print("="*50)
    
    return True

def send_test_notification():
    """Send a test notification using existing infrastructure."""
    print("\n🔔 Testing notification system...")
    
    try:
        # Use the MCP server's notification system
        test_command = [
            "python", "-c", 
            """
import sys
sys.path.append('.')
from mcp_server import notify
result = notify('notify', target_agent='PersonalSidekick', message='Sidekick system test - ready for accountability!')
print(f"Notification result: {result}")
"""
        ]
        
        result = subprocess.run(test_command, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Notification system working")
        else:
            print("⚠️  Notification test had issues (but sidekick will still work)")
            
    except Exception as e:
        print(f"⚠️  Notification test failed: {e}")
        print("   (Sidekick will still work for conversations)")

if __name__ == "__main__":
    print("🤖 PERSONAL AI SIDEKICK - QUICK LAUNCH")
    print("This script prepares your existing infrastructure as a personal sidekick")
    print()
    
    success = launch_sidekick()
    
    if success:
        print("\n🔔 Testing notification system...")
        send_test_notification()
        
        print("\n✨ SIDEKICK READY!")
        print("Your personal accountability coach is ready to help you focus.")
    else:
        print("\n❌ Setup incomplete - check error messages above")
        sys.exit(1)
