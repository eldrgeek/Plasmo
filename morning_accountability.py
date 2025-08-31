#!/usr/bin/env python3
"""
🌅 Morning Routine Accountability System
Uses existing MCP notification infrastructure for daily check-ins
"""

from datetime import datetime, time
import sys
import os

# Add current directory to path for MCP tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def send_morning_reminder():
    """Send morning accountability reminder using existing notify system."""
    
    # Import the notification function from existing MCP server
    try:
        from packages.mcp_server.mcp_server import create_notification
        
        current_time = datetime.now()
        wake_time_window = "5:30-7:30 AM"
        
        message = f"""🌅 GOOD MORNING, MIKE! Your PersonalSidekick accountability check-in:

⏰ Current time: {current_time.strftime('%I:%M %p')}
🎯 Today's focus: What's the single most important thing?
🥋 Martial arts: Minimum 1 hour planned?
🚿 Cold shower: Ready to restart this habit?

Reply with your priorities for today. Remember: CONVERGENT execution, not divergent exploration!

Your Sidekick 🤖"""
        
        # Send notification to main agent
        result = create_notification(
            target_agent="Plasmo",
            message=message,
            sender="PersonalSidekick_MorningRoutine"
        )
        
        print(f"✅ Morning reminder sent: {result['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending morning reminder: {e}")
        return False

def check_time_window():
    """Check if current time is in morning accountability window."""
    now = datetime.now().time()
    start_time = time(5, 30)  # 5:30 AM
    end_time = time(7, 30)    # 7:30 AM
    
    return start_time <= now <= end_time

if __name__ == "__main__":
    print("🌅 Morning Routine Accountability System")
    
    if check_time_window():
        print("⏰ Within morning window (5:30-7:30 AM) - sending reminder")
        send_morning_reminder()
    else:
        current_time = datetime.now().strftime('%I:%M %p')
        print(f"⏰ Current time: {current_time}")
        print("💡 Morning reminder scheduled for 5:30-7:30 AM window")
        print("🧪 Sending test reminder now...")
        send_morning_reminder()
