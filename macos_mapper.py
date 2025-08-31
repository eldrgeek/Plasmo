#!/usr/bin/env python3
"""
macOS Desktop and App Mapper
Maps all desktops/spaces and their applications using native macOS tools
"""

import subprocess
import json
import sys
import re
from collections import defaultdict

def run_applescript(script):
    """Run an AppleScript and return the result"""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running AppleScript: {e}")
        return None

def run_shell_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running shell command: {e}")
        return None

def get_running_apps():
    """Get all running applications"""
    script = '''
    tell application "System Events"
        set appList to {}
        repeat with proc in application processes
            if background only of proc is false then
                set end of appList to {name of proc, visible of proc, frontmost of proc}
            end if
        end repeat
        return appList
    end tell
    '''
    
    result = run_applescript(script)
    if not result:
        return []
    
    apps = []
    # Parse the AppleScript result
    if result and result != "":
        # Remove outer braces and split by }, {
        result = result.strip("{}")
        if result:
            app_entries = re.split(r'},\s*{', result)
            for entry in app_entries:
                entry = entry.strip("{}")
                parts = [part.strip().strip('"') for part in entry.split(',')]
                if len(parts) >= 3:
                    apps.append({
                        'name': parts[0],
                        'visible': parts[1].lower() == 'true',
                        'frontmost': parts[2].lower() == 'true'
                    })
    
    return apps

def get_window_info():
    """Get window information for visible applications"""
    script = '''
    tell application "System Events"
        set windowList to {}
        repeat with proc in application processes
            if background only of proc is false then
                try
                    repeat with win in windows of proc
                        if exists win then
                            set end of windowList to {name of proc, title of win, visible of win, (position of win), (size of win)}
                        end if
                    end repeat
                end try
            end if
        end repeat
        return windowList
    end tell
    '''
    
    result = run_applescript(script)
    if not result:
        return []
    
    windows = []
    if result and result != "":
        # This is a simplified parser - AppleScript list parsing can be complex
        try:
            # Remove outer braces
            result = result.strip("{}")
            if result:
                # Split by major delimiters
                window_entries = re.split(r'},\s*{', result)
                for entry in window_entries:
                    entry = entry.strip("{}")
                    # Basic parsing - this may need refinement
                    if entry:
                        windows.append({'raw': entry})
        except:
            pass
    
    return windows

def get_current_space_info():
    """Get current space/desktop information"""
    script = '''
    tell application "System Events"
        tell dock preferences
            set spacesCount to count of spaces
        end tell
    end tell
    '''
    
    # This is limited as macOS doesn't expose detailed space info via AppleScript
    return run_applescript(script)

def get_dock_apps():
    """Get applications in the Dock"""
    script = '''
    tell application "System Events"
        tell dock preferences
            set dockApps to {}
            try
                repeat with dockItem in dock items
                    set end of dockApps to name of dockItem
                end repeat
            end try
            return dockApps
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    if result:
        # Parse the list result
        apps = result.strip("{}")
        if apps:
            return [app.strip().strip('"') for app in apps.split(',')]
    return []

def get_system_info():
    """Get basic system information"""
    # Get macOS version
    version = run_shell_command("sw_vers -productVersion")
    
    # Get display info
    displays = run_shell_command("system_profiler SPDisplaysDataType -json")
    display_count = 1
    try:
        if displays:
            display_data = json.loads(displays)
            display_count = len(display_data.get('SPDisplaysDataType', [{}])[0].get('spdisplays_ndrvs', []))
    except:
        pass
    
    return {
        'version': version,
        'display_count': display_count
    }

def main():
    print("🖥️  macOS Desktop and App Mapper")
    print("=" * 50)
    
    # Get system information
    system_info = get_system_info()
    print(f"\n📊 System Overview:")
    print(f"  macOS Version: {system_info['version']}")
    print(f"  Displays: {system_info['display_count']}")
    
    # Get running applications
    print("\n🔄 Getting running applications...")
    apps = get_running_apps()
    
    if not apps:
        print("Could not retrieve application information.")
        return
    
    visible_apps = [app for app in apps if app['visible']]
    hidden_apps = [app for app in apps if not app['visible']]
    frontmost_app = next((app for app in apps if app['frontmost']), None)
    
    print(f"  Total Running Apps: {len(apps)}")
    print(f"  Visible Apps: {len(visible_apps)}")
    print(f"  Hidden Apps: {len(hidden_apps)}")
    
    if frontmost_app:
        print(f"  🔸 Active App: {frontmost_app['name']}")
    
    # Display visible applications
    print(f"\n👁️  Visible Applications:")
    print("-" * 30)
    
    for app in sorted(visible_apps, key=lambda x: x['name'].lower()):
        status = "🔸 ACTIVE" if app['frontmost'] else ""
        print(f"  • {app['name']} {status}")
    
    # Display hidden applications
    if hidden_apps:
        print(f"\n📦 Hidden Applications:")
        print("-" * 30)
        
        for app in sorted(hidden_apps, key=lambda x: x['name'].lower()):
            print(f"  • {app['name']}")
    
    # Get Dock applications
    print(f"\n🚢 Applications in Dock:")
    print("-" * 30)
    dock_apps = get_dock_apps()
    
    if dock_apps:
        for app in dock_apps:
            # Check if the app is currently running
            is_running = any(running_app['name'] == app for running_app in apps)
            status = "🔹 RUNNING" if is_running else ""
            print(f"  • {app} {status}")
    else:
        print("  Could not retrieve Dock information")
    
    # Get window information (basic)
    print(f"\n🪟 Window Information:")
    print("-" * 30)
    windows = get_window_info()
    
    if windows:
        print(f"  Total Windows: {len(windows)}")
        # Window details are complex to parse from AppleScript
        print("  (Detailed window info requires advanced parsing)")
    else:
        print("  Could not retrieve detailed window information")
    
    # Additional system information
    print(f"\n🔧 Additional Tools Available:")
    print("-" * 30)
    
    # Check for window management tools
    tools_to_check = ['yabai', 'amethyst', 'rectangle', 'spectacle', 'hammerspoon']
    for tool in tools_to_check:
        result = run_shell_command(f"which {tool}")
        if result:
            print(f"  ✅ {tool}: {result}")
        else:
            print(f"  ❌ {tool}: Not installed")
    
    print(f"\n✅ Mapping complete!")
    print("\n💡 Note: For more detailed window and space management,")
    print("   consider installing a window manager like Yabai, Rectangle, or Amethyst.")

if __name__ == "__main__":
    main()
