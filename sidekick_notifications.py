#!/usr/bin/env python3
"""
🤖 PersonalSidekick - Native Mac Notification System
Uses built-in macOS notifications for accountability reminders
"""

import subprocess
import sys
from datetime import datetime

def send_mac_notification(title, message, sound="Ping"):
    """Send native macOS notification."""
    script = f'''
    display notification "{message}" with title "{title}" sound name "{sound}"
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Notification sent: {title}")
            return True
        else:
            print(f"❌ Notification failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

def morning_accountability_reminder():
    """Send morning accountability reminder."""
    current_time = datetime.now().strftime('%I:%M %p')
    
    title = "🌅 PersonalSidekick - Morning Check-in"
    message = f"Good morning! Time: {current_time}. What's your single most important focus today? 🎯"
    
    return send_mac_notification(title, message, "Glass")

def focus_redirect_notification():
    """Send focus redirect notification."""
    title = "🎯 PersonalSidekick - Focus Check"
    message = "I notice you might be getting distracted. What's the single most important thing you should focus on right now?"
    
    return send_mac_notification(title, message, "Ping")

def martial_arts_reminder():
    """Send martial arts practice reminder."""
    title = "🥋 PersonalSidekick - Martial Arts"
    message = "Time for your minimum 1-hour martial arts practice! External structure works - where will you practice?"
    
    return send_mac_notification(title, message, "Hero")

if __name__ == "__main__":
    print("🤖 PersonalSidekick Notification Test")
    
    # Test all notification types
    morning_accountability_reminder()
    focus_redirect_notification() 
    martial_arts_reminder()
    
    print("\n✅ If you saw 3 Mac notifications, your sidekick accountability system is READY!")
