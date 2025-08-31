#!/usr/bin/env python3
"""
Yabai vs OSAScript Application Information Comparison
Shows what each method can and cannot see about running applications
"""

import subprocess
import json
import re

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
    except:
        return None

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
    except:
        return None

def get_yabai_info():
    """Get application info from Yabai"""
    print("🖥️  YABAI INFORMATION")
    print("=" * 60)
    print("(Window Manager Perspective - Only Manageable Windows)")
    
    # Get windows
    windows = run_yabai_command("--windows")
    if not windows:
        print("❌ Could not get Yabai window information")
        return {}
    
    # Group by application
    yabai_apps = {}
    for window in windows:
        app_name = window.get('app', 'Unknown')
        if app_name not in yabai_apps:
            yabai_apps[app_name] = {
                'windows': [],
                'spaces': set(),
                'states': set()
            }
        
        yabai_apps[app_name]['windows'].append({
            'title': window.get('title', 'No Title'),
            'space': window.get('space'),
            'is_floating': window.get('is-floating'),
            'has_focus': window.get('has-focus'),
            'is_minimized': window.get('is-minimized'),
            'frame': window.get('frame', {}),
            'pid': window.get('pid')
        })
        
        yabai_apps[app_name]['spaces'].add(window.get('space'))
        
        if window.get('is-floating'):
            yabai_apps[app_name]['states'].add('floating')
        if window.get('has-focus'):
            yabai_apps[app_name]['states'].add('focused')
        if window.get('is-minimized'):
            yabai_apps[app_name]['states'].add('minimized')
    
    print(f"\n📊 Found {len(yabai_apps)} applications with manageable windows:")
    print(f"📊 Total manageable windows: {len(windows)}")
    
    for app_name, info in sorted(yabai_apps.items()):
        spaces_list = sorted(list(info['spaces']))
        states_list = list(info['states'])
        
        print(f"\n• {app_name}")
        print(f"  Windows: {len(info['windows'])}")
        print(f"  Spaces: {spaces_list}")
        print(f"  States: {states_list if states_list else ['tiled']}")
        
        # Show window details
        for i, win in enumerate(info['windows'][:2]):  # Show first 2 windows
            title = win['title'][:40] + "..." if len(win['title']) > 40 else win['title']
            print(f"    [{i+1}] {title} (Space {win['space']})")
        
        if len(info['windows']) > 2:
            print(f"    ... and {len(info['windows'])-2} more windows")
    
    return yabai_apps

def get_osascript_info():
    """Get application info from AppleScript/System Events"""
    print(f"\n\n🍎 OSASCRIPT/APPLESCRIPT INFORMATION")
    print("=" * 60)
    print("(System Events Perspective - All Running Processes)")
    
    # Get all application processes
    script = '''
    tell application "System Events"
        set appList to {}
        repeat with proc in application processes
            if background only of proc is false then
                try
                    set windowCount to count of windows of proc
                    set end of appList to {name of proc, visible of proc, frontmost of proc, windowCount, unix id of proc}
                end try
            end if
        end repeat
        return appList
    end tell
    '''
    
    result = run_applescript(script)
    if not result:
        print("❌ Could not get AppleScript application information")
        return {}
    
    osascript_apps = {}
    
    # Parse the AppleScript result
    if result and result != "":
        # Remove outer braces and parse
        result = result.strip("{}")
        if result:
            try:
                # Split by major delimiters - AppleScript parsing is tricky
                app_entries = re.split(r'},\s*{', result)
                for entry in app_entries:
                    entry = entry.strip("{}")
                    parts = [part.strip().strip('"') for part in entry.split(',')]
                    if len(parts) >= 5:
                        app_name = parts[0]
                        is_visible = parts[1].lower() == 'true'
                        is_frontmost = parts[2].lower() == 'true'
                        window_count = int(parts[3]) if parts[3].isdigit() else 0
                        pid = int(parts[4]) if parts[4].isdigit() else 0
                        
                        osascript_apps[app_name] = {
                            'visible': is_visible,
                            'frontmost': is_frontmost,
                            'window_count': window_count,
                            'pid': pid
                        }
            except Exception as e:
                print(f"⚠️  AppleScript parsing error: {e}")
    
    # Get additional system information
    dock_script = '''
    tell application "System Events"
        tell dock preferences
            try
                set dockItems to name of dock items
                return dockItems
            end try
        end tell
    end tell
    '''
    
    dock_result = run_applescript(dock_script)
    dock_apps = []
    if dock_result:
        dock_result = dock_result.strip("{}")
        if dock_result:
            dock_apps = [app.strip().strip('"') for app in dock_result.split(',')]
    
    print(f"\n📊 Found {len(osascript_apps)} visible application processes:")
    
    visible_apps = [name for name, info in osascript_apps.items() if info['visible']]
    hidden_apps = [name for name, info in osascript_apps.items() if not info['visible']]
    frontmost_app = next((name for name, info in osascript_apps.items() if info['frontmost']), None)
    
    print(f"📊 Visible apps: {len(visible_apps)}")
    print(f"📊 Hidden apps: {len(hidden_apps)}")
    print(f"📊 Frontmost app: {frontmost_app}")
    print(f"📊 Apps in Dock: {len(dock_apps)}")
    
    print(f"\n👁️  Visible Applications:")
    for app_name in sorted(visible_apps):
        info = osascript_apps[app_name]
        status = []
        if info['frontmost']:
            status.append('FRONTMOST')
        if app_name in dock_apps:
            status.append('IN_DOCK')
        
        status_str = f" ({', '.join(status)})" if status else ""
        print(f"  • {app_name} - {info['window_count']} windows - PID {info['pid']}{status_str}")
    
    if hidden_apps:
        print(f"\n📦 Hidden Applications (first 10):")
        for app_name in sorted(hidden_apps[:10]):
            info = osascript_apps[app_name]
            print(f"  • {app_name} - PID {info['pid']}")
    
    return osascript_apps, dock_apps

def compare_information(yabai_apps, osascript_apps):
    """Compare what each method can see"""
    print(f"\n\n🔍 COMPARISON ANALYSIS")
    print("=" * 60)
    
    yabai_app_names = set(yabai_apps.keys())
    osascript_app_names = set(osascript_apps[0].keys()) if osascript_apps else set()
    
    # Apps seen by both
    common_apps = yabai_app_names & osascript_app_names
    
    # Apps only seen by Yabai
    yabai_only = yabai_app_names - osascript_app_names
    
    # Apps only seen by AppleScript
    osascript_only = osascript_app_names - yabai_app_names
    
    print(f"\n📊 Summary:")
    print(f"  Apps seen by BOTH: {len(common_apps)}")
    print(f"  Apps ONLY by Yabai: {len(yabai_only)}")
    print(f"  Apps ONLY by AppleScript: {len(osascript_only)}")
    
    if common_apps:
        print(f"\n✅ Applications seen by BOTH methods:")
        for app in sorted(common_apps):
            yabai_windows = len(yabai_apps[app]['windows'])
            osascript_windows = osascript_apps[0][app]['window_count'] if osascript_apps else 0
            print(f"  • {app} - Yabai: {yabai_windows} windows, AppleScript: {osascript_windows} windows")
    
    if yabai_only:
        print(f"\n🖥️  Applications ONLY seen by Yabai:")
        for app in sorted(yabai_only):
            print(f"  • {app} ({len(yabai_apps[app]['windows'])} windows)")
    
    if osascript_only:
        print(f"\n🍎 Applications ONLY seen by AppleScript:")
        for app in sorted(list(osascript_only)[:10]):  # Show first 10
            if osascript_apps:
                info = osascript_apps[0][app]
                print(f"  • {app} ({info['window_count']} windows, {'visible' if info['visible'] else 'hidden'})")
    
    print(f"\n💡 Key Differences:")
    print("=" * 30)
    print("📊 YABAI can see:")
    print("  ✅ Window positions, sizes, and frames")
    print("  ✅ Window tiling/floating states")
    print("  ✅ Which space/desktop each window is on")
    print("  ✅ Window focus states")
    print("  ✅ Detailed window management metadata")
    print("  ❌ Background/hidden applications")
    print("  ❌ Menu bar apps without windows")
    print("  ❌ System processes")
    
    print("📊 APPLESCRIPT can see:")
    print("  ✅ All running application processes")
    print("  ✅ Background and hidden applications")
    print("  ✅ System applications and utilities")
    print("  ✅ Applications in the Dock")
    print("  ✅ Process IDs and visibility states")
    print("  ✅ Frontmost application")
    print("  ❌ Window positions and frames")
    print("  ❌ Tiling/floating states")
    print("  ❌ Space/desktop assignments")

def main():
    print("🔍 Yabai vs OSAScript Application Information Comparison")
    print("Analyzing what each method can see about your running applications")
    print("=" * 80)
    
    # Get information from both methods
    yabai_apps = get_yabai_info()
    osascript_info = get_osascript_info()
    
    # Compare the results
    compare_information(yabai_apps, osascript_info)
    
    print(f"\n🎯 PRACTICAL IMPLICATIONS:")
    print("=" * 30)
    print("Use YABAI when you need:")
    print("  • Window management and positioning")
    print("  • Tiling window manager functionality")
    print("  • Information about which desktop/space windows are on")
    print("  • Fast, structured window data")
    
    print("\nUse APPLESCRIPT when you need:")
    print("  • Complete list of all running applications")
    print("  • Information about background processes")
    print("  • System integration and app launching")
    print("  • Dock and menu bar app information")

if __name__ == "__main__":
    main()
