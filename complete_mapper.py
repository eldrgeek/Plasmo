#!/usr/bin/env python3
"""
Complete Desktop and App Mapper
Combines Yabai window management data with native macOS application info
"""

import subprocess
import json
import sys
import re
import os
from collections import defaultdict

def run_yabai_command(command):
    """Run a yabai command and return parsed JSON result"""
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/yabai", "-m", "query"] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running yabai command: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except FileNotFoundError:
        print("Error: Yabai not found at /opt/homebrew/bin/yabai")
        return None

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_running_apps_ps():
    """Get running applications using ps command"""
    result = run_command("ps aux | grep -E '\\.app|/Applications' | grep -v grep")
    
    apps = []
    if result:
        lines = result.split('\n')
        app_names = set()
        
        for line in lines:
            if '.app' in line:
                app_match = re.search(r'([^/]+\.app)', line)
                if app_match:
                    app_name = app_match.group(1).replace('.app', '')
                    app_names.add(app_name)
        
        apps = list(app_names)
    
    return sorted(apps)

def get_yabai_info():
    """Get comprehensive Yabai information"""
    spaces = run_yabai_command("--spaces")
    windows = run_yabai_command("--windows")
    displays = run_yabai_command("--displays")
    
    return {
        'spaces': spaces or [],
        'windows': windows or [],
        'displays': displays or []
    }

def main():
    print("🖥️  Complete Desktop and App Mapper")
    print("🔗  Yabai + Native macOS Information")
    print("=" * 60)
    
    # Get Yabai information
    yabai_info = get_yabai_info()
    spaces = yabai_info['spaces']
    windows = yabai_info['windows']
    displays = yabai_info['displays']
    
    if not spaces:
        print("❌ Could not retrieve Yabai information. Is Yabai running?")
        print("   Try: brew services start yabai")
        return
    
    # Get native macOS app info
    running_apps = get_running_apps_ps()
    
    print(f"\n📊 System Overview:")
    print(f"  Displays: {len(displays)}")
    print(f"  Yabai Desktop Spaces: {len(spaces)}")
    print(f"  Yabai Managed Windows: {len(windows)}")
    print(f"  Total Running Apps: {len(running_apps)}")
    
    # Create mapping of space ID to windows
    space_windows = defaultdict(list)
    for window in windows:
        space_id = window.get('space')
        if space_id:
            space_windows[space_id].append(window)
    
    # Get apps that have Yabai-managed windows
    yabai_managed_apps = set()
    for window in windows:
        app_name = window.get('app')
        if app_name:
            yabai_managed_apps.add(app_name)
    
    # Sort spaces by display and index
    spaces.sort(key=lambda x: (x.get('display', 0), x.get('index', 0)))
    
    # Display header
    current_display = None
    
    print(f"\n🖥️  YABAI DESKTOP SPACES")
    print("=" * 40)
    
    for space in spaces:
        space_id = space.get('id')
        space_index = space.get('index', 0)
        space_label = space.get('label', f"Space {space_index}")
        display_index = space.get('display', 1)
        is_focused = space.get('has-focus', False)
        is_visible = space.get('is-visible', False)
        
        # Display header when we switch to a new display
        if current_display != display_index:
            current_display = display_index
            display_info = next((d for d in displays if d.get('index') == display_index), {})
            display_name = display_info.get('label', f"Display {display_index}")
            print(f"\n🖥️  {display_name}")
            if display_info:
                frame = display_info.get('frame', {})
                if frame:
                    print(f"    Resolution: {frame.get('w', '?')} x {frame.get('h', '?')}")
            print("-" * 30)
        
        # Space status indicators
        status_indicators = []
        if is_focused:
            status_indicators.append("🔵 FOCUSED")
        if is_visible:
            status_indicators.append("👁️  VISIBLE")
        
        status_text = " " + " ".join(status_indicators) if status_indicators else ""
        
        # Space header
        space_windows_list = space_windows.get(space_id, [])
        window_count = len(space_windows_list)
        
        print(f"\n📱 Desktop {space_index}: {space_label}{status_text}")
        print(f"   Managed Windows: {window_count}")
        
        if window_count == 0:
            print("   (No managed windows)")
        else:
            # Group windows by app
            app_windows = defaultdict(list)
            for window in space_windows_list:
                app_name = window.get('app', 'Unknown')
                app_windows[app_name].append(window)
            
            # Display apps and their windows
            for app_name, app_window_list in sorted(app_windows.items()):
                if len(app_window_list) == 1:
                    window = app_window_list[0]
                    title = window.get('title', 'No Title')
                    if len(title) > 45:
                        title = title[:42] + "..."
                    
                    # Window state indicators
                    indicators = []
                    if window.get('has-focus'):
                        indicators.append("🔸")
                    if window.get('is-minimized'):
                        indicators.append("📦")
                    if window.get('is-floating'):
                        indicators.append("🎈")
                    
                    indicator_text = "".join(indicators) + " " if indicators else ""
                    print(f"   • {indicator_text}{app_name}: {title}")
                else:
                    print(f"   • {app_name} ({len(app_window_list)} windows)")
                    for window in app_window_list:
                        title = window.get('title', 'No Title')
                        if len(title) > 40:
                            title = title[:37] + "..."
                        
                        # Window state indicators
                        indicators = []
                        if window.get('has-focus'):
                            indicators.append("🔸")
                        if window.get('is-minimized'):
                            indicators.append("📦")
                        if window.get('is-floating'):
                            indicators.append("🎈")
                        
                        indicator_text = "".join(indicators) + " " if indicators else ""
                        print(f"     - {indicator_text}{title}")
    
    # Summary of window states
    floating_windows = [w for w in windows if w.get('is-floating')]
    minimized_windows = [w for w in windows if w.get('is-minimized')]
    
    if floating_windows or minimized_windows:
        print(f"\n📋 Window States Summary:")
        if floating_windows:
            print(f"   🎈 Floating windows: {len(floating_windows)}")
        if minimized_windows:
            print(f"   📦 Minimized windows: {len(minimized_windows)}")
    
    # Show comparison with all running apps
    print(f"\n📱 APPLICATION COMPARISON")
    print("=" * 40)
    
    unmanaged_apps = set(running_apps) - yabai_managed_apps
    
    print(f"\n✅ Yabai-Managed Applications ({len(yabai_managed_apps)}):")
    for app in sorted(yabai_managed_apps):
        window_count = len([w for w in windows if w.get('app') == app])
        print(f"   • {app} ({window_count} windows)")
    
    print(f"\n⚪ Unmanaged Applications ({len(unmanaged_apps)}):")
    print("   (Running but not managed by Yabai)")
    for app in sorted(list(unmanaged_apps)[:15]):  # Show first 15
        print(f"   • {app}")
    
    if len(unmanaged_apps) > 15:
        print(f"   ... and {len(unmanaged_apps) - 15} more")
    
    print(f"\n🔧 YABAI CONFIGURATION CHECK")
    print("=" * 40)
    
    # Check yabai service status
    service_status = run_command("brew services list | grep yabai")
    if service_status:
        print(f"   Service Status: {service_status}")
    
    # Check yabai config
    config_path = os.path.expanduser("~/.yabairc")
    if os.path.exists(config_path):
        print(f"   ✅ Config file found: ~/.yabairc")
    else:
        print(f"   ❌ No config file found at ~/.yabairc")
    
    print(f"\n✅ Complete mapping finished!")
    
    print(f"\n💡 Tips:")
    print("   • Yabai only manages certain window types")
    print("   • System apps, menu bar apps, and background processes are typically unmanaged")
    print("   • Use 'yabai -m config' to see current configuration")
    print("   • Check ~/.yabairc for custom rules and settings")

if __name__ == "__main__":
    main()
