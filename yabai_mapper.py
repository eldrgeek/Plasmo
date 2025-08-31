#!/usr/bin/env python3
"""
Yabai Desktop and App Mapper
Maps all desktops/spaces and their applications using Yabai window manager
"""

import subprocess
import json
import sys
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
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except FileNotFoundError:
        print("Error: Yabai not found. Make sure Yabai is installed and in your PATH.")
        return None

def get_spaces():
    """Get all spaces/desktops information"""
    return run_yabai_command("--spaces")

def get_windows():
    """Get all windows information"""
    return run_yabai_command("--windows")

def get_displays():
    """Get display information"""
    return run_yabai_command("--displays")

def format_app_info(window):
    """Format window/app information for display"""
    app_name = window.get('app', 'Unknown')
    title = window.get('title', 'No Title')
    
    # Truncate long titles
    if len(title) > 50:
        title = title[:47] + "..."
    
    return f"  • {app_name}: {title}"

def main():
    print("🖥️  Yabai Desktop and App Mapper")
    print("=" * 50)
    
    # Get system information
    spaces = get_spaces()
    windows = get_windows()
    displays = get_displays()
    
    if not spaces or not windows:
        print("Failed to retrieve information from Yabai.")
        sys.exit(1)
    
    # Create mapping of space ID to windows
    space_windows = defaultdict(list)
    for window in windows:
        space_id = window.get('space')
        if space_id:
            space_windows[space_id].append(window)
    
    # Create mapping of display index to display info
    display_map = {}
    if displays:
        for display in displays:
            display_map[display.get('index')] = display
    
    # Sort spaces by display and index
    spaces.sort(key=lambda x: (x.get('display', 0), x.get('index', 0)))
    
    print(f"\n📊 System Overview:")
    print(f"  Displays: {len(displays) if displays else 'Unknown'}")
    print(f"  Desktop Spaces: {len(spaces)}")
    print(f"  Total Windows: {len(windows)}")
    
    current_display = None
    
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
            display_info = display_map.get(display_index, {})
            display_name = display_info.get('label', f"Display {display_index}")
            print(f"\n🖥️  {display_name}")
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
        print(f"   Windows: {window_count}")
        
        if window_count == 0:
            print("   (Empty desktop)")
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
                    if len(title) > 50:
                        title = title[:47] + "..."
                    
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
                        print(f"     - {indicator_text}{title}")
    
    # Summary of floating windows
    floating_windows = [w for w in windows if w.get('is-floating')]
    minimized_windows = [w for w in windows if w.get('is-minimized')]
    
    if floating_windows or minimized_windows:
        print(f"\n📋 Window States Summary:")
        if floating_windows:
            print(f"   🎈 Floating windows: {len(floating_windows)}")
        if minimized_windows:
            print(f"   📦 Minimized windows: {len(minimized_windows)}")
    
    print(f"\n✅ Mapping complete!")

if __name__ == "__main__":
    main()
