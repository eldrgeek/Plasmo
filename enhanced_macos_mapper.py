#!/usr/bin/env python3
"""
Enhanced macOS Desktop and App Mapper
Uses multiple approaches to map desktops/spaces and applications
"""

import subprocess
import json
import sys
import re
import os
from collections import defaultdict

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
    # Get running processes that look like applications
    result = run_command("ps aux | grep -E '\\.app|/Applications' | grep -v grep")
    
    apps = []
    if result:
        lines = result.split('\n')
        app_names = set()
        
        for line in lines:
            # Extract app names from paths
            if '.app' in line:
                # Find .app in the path
                app_match = re.search(r'([^/]+\.app)', line)
                if app_match:
                    app_name = app_match.group(1).replace('.app', '')
                    app_names.add(app_name)
        
        apps = list(app_names)
    
    return sorted(apps)

def get_dock_apps_plist():
    """Get Dock applications from plist file"""
    try:
        plist_path = os.path.expanduser("~/Library/Preferences/com.apple.dock.plist")
        if os.path.exists(plist_path):
            result = run_command(f"plutil -convert json -o - '{plist_path}'")
            if result:
                dock_data = json.loads(result)
                persistent_apps = dock_data.get('persistent-apps', [])
                
                apps = []
                for app in persistent_apps:
                    tile_data = app.get('tile-data', {})
                    file_data = tile_data.get('file-data', {})
                    name = file_data.get('_CFURLString', '')
                    
                    if name:
                        # Extract app name from path
                        app_name = os.path.basename(name).replace('.app', '')
                        apps.append(app_name)
                
                return apps
    except:
        pass
    
    return []

def get_applications_folder():
    """Get applications from /Applications folder"""
    apps = []
    try:
        result = run_command("ls /Applications")
        if result:
            for line in result.split('\n'):
                if line.endswith('.app'):
                    apps.append(line.replace('.app', ''))
    except:
        pass
    
    return sorted(apps)

def get_system_info():
    """Get comprehensive system information"""
    info = {}
    
    # macOS version
    info['version'] = run_command("sw_vers -productVersion")
    info['build'] = run_command("sw_vers -buildVersion")
    
    # Hardware info
    info['model'] = run_command("sysctl -n hw.model")
    info['cpu'] = run_command("sysctl -n machdep.cpu.brand_string")
    
    # Memory info
    memory_gb = run_command("sysctl -n hw.memsize")
    if memory_gb:
        try:
            memory_gb = int(memory_gb) // (1024**3)
            info['memory'] = f"{memory_gb} GB"
        except:
            info['memory'] = "Unknown"
    
    # Display info
    displays = run_command("system_profiler SPDisplaysDataType | grep Resolution")
    if displays:
        display_lines = displays.split('\n')
        info['displays'] = len(display_lines)
        info['resolutions'] = [line.strip() for line in display_lines]
    else:
        info['displays'] = 1
        info['resolutions'] = []
    
    return info

def get_homebrew_info():
    """Check for Homebrew and installed packages"""
    brew_path = run_command("which brew")
    if brew_path:
        # Get installed window managers via Homebrew
        brew_list = run_command("brew list --formula")
        if brew_list:
            wm_tools = ['yabai', 'amethyst', 'rectangle', 'spectacle', 'hammerspoon', 'phoenix', 'slate']
            installed_wms = [tool for tool in wm_tools if tool in brew_list]
            return {
                'installed': True,
                'path': brew_path,
                'window_managers': installed_wms
            }
    
    return {'installed': False}

def get_active_window_info():
    """Get information about the currently active window"""
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        set frontAppWindows to count of windows of application process frontApp
        return {frontApp, frontAppWindows}
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if output:
            # Parse the result
            output = output.strip("{}")
            parts = [part.strip().strip('"') for part in output.split(',')]
            if len(parts) >= 2:
                return {
                    'app': parts[0],
                    'windows': parts[1]
                }
    except:
        pass
    
    return None

def check_mission_control():
    """Check Mission Control / Spaces configuration"""
    # Check if Mission Control is enabled
    mc_enabled = run_command("defaults read com.apple.dock mcx-expose-disabled 2>/dev/null || echo '0'")
    
    # Check spaces configuration
    spaces_spans = run_command("defaults read com.apple.spaces spans-displays 2>/dev/null || echo '1'")
    
    return {
        'mission_control_enabled': mc_enabled != '1',
        'spaces_span_displays': spaces_spans == '1'
    }

def main():
    print("🖥️  Enhanced macOS Desktop and App Mapper")
    print("=" * 60)
    
    # Get comprehensive system information
    system_info = get_system_info()
    print(f"\n💻 System Information:")
    print(f"  macOS Version: {system_info.get('version', 'Unknown')}")
    print(f"  Build: {system_info.get('build', 'Unknown')}")
    print(f"  Model: {system_info.get('model', 'Unknown')}")
    print(f"  CPU: {system_info.get('cpu', 'Unknown')}")
    print(f"  Memory: {system_info.get('memory', 'Unknown')}")
    print(f"  Displays: {system_info.get('displays', 'Unknown')}")
    
    if system_info.get('resolutions'):
        for i, res in enumerate(system_info['resolutions'], 1):
            print(f"    Display {i}: {res}")
    
    # Check Mission Control/Spaces
    mc_info = check_mission_control()
    print(f"\n🚀 Mission Control & Spaces:")
    print(f"  Mission Control Enabled: {'Yes' if mc_info['mission_control_enabled'] else 'No'}")
    print(f"  Spaces Span Displays: {'Yes' if mc_info['spaces_span_displays'] else 'No'}")
    
    # Get active window information
    active_window = get_active_window_info()
    if active_window:
        print(f"\n🔸 Currently Active:")
        print(f"  App: {active_window['app']}")
        print(f"  Windows: {active_window['windows']}")
    
    # Get running applications using ps
    print(f"\n🔄 Running Applications (via process list):")
    print("-" * 40)
    running_apps = get_running_apps_ps()
    
    if running_apps:
        for i, app in enumerate(running_apps, 1):
            print(f"  {i:2d}. {app}")
        print(f"\n  Total: {len(running_apps)} applications")
    else:
        print("  No applications detected via process list")
    
    # Get Dock applications
    print(f"\n🚢 Applications in Dock:")
    print("-" * 40)
    dock_apps = get_dock_apps_plist()
    
    if dock_apps:
        for i, app in enumerate(dock_apps, 1):
            # Check if app is currently running
            is_running = app in running_apps
            status = " 🟢" if is_running else " ⚪"
            print(f"  {i:2d}. {app}{status}")
        print(f"\n  Total: {len(dock_apps)} applications in Dock")
        print("  🟢 = Running, ⚪ = Not Running")
    else:
        print("  Could not read Dock preferences")
    
    # Get installed applications
    print(f"\n📱 Installed Applications (/Applications):")
    print("-" * 40)
    installed_apps = get_applications_folder()
    
    if installed_apps:
        # Show first 20 applications
        display_apps = installed_apps[:20]
        for i, app in enumerate(display_apps, 1):
            is_running = app in running_apps
            is_in_dock = app in dock_apps
            
            status = ""
            if is_running:
                status += " 🟢"
            if is_in_dock:
                status += " 🚢"
            
            print(f"  {i:2d}. {app}{status}")
        
        if len(installed_apps) > 20:
            print(f"  ... and {len(installed_apps) - 20} more applications")
        
        print(f"\n  Total: {len(installed_apps)} applications installed")
        print("  🟢 = Running, 🚢 = In Dock")
    
    # Check for window management tools
    print(f"\n🔧 Window Management Tools:")
    print("-" * 40)
    
    # Check Homebrew
    homebrew_info = get_homebrew_info()
    if homebrew_info['installed']:
        print(f"  ✅ Homebrew installed at: {homebrew_info['path']}")
        if homebrew_info['window_managers']:
            print("  📦 Installed window managers:")
            for wm in homebrew_info['window_managers']:
                print(f"    • {wm}")
        else:
            print("  📦 No window managers installed via Homebrew")
    else:
        print("  ❌ Homebrew not installed")
    
    # Check for common window managers
    wm_tools = {
        'yabai': 'Advanced tiling window manager',
        'rectangle': 'Window snapping tool',
        'amethyst': 'Automatic tiling window manager', 
        'spectacle': 'Window organization tool',
        'hammerspoon': 'Automation framework',
        'phoenix': 'Lightweight scriptable window manager'
    }
    
    print(f"\n  🔍 System-wide tool check:")
    for tool, description in wm_tools.items():
        path = run_command(f"which {tool}")
        if path:
            print(f"    ✅ {tool}: {path}")
            print(f"       ({description})")
        else:
            print(f"    ❌ {tool}: Not installed")
    
    print(f"\n✅ Enhanced mapping complete!")
    
    # Show recommendations
    print(f"\n💡 Recommendations:")
    if not homebrew_info['installed']:
        print("  • Install Homebrew for easy package management")
        print("    /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    
    if not homebrew_info.get('window_managers'):
        print("  • For advanced window management, consider:")
        print("    brew install yabai           # Advanced tiling")
        print("    brew install rectangle       # Simple window snapping")
        print("    brew install amethyst        # Automatic tiling")
    
    print("  • Enable accessibility permissions for enhanced app control")
    print("  • System Settings > Privacy & Security > Accessibility")

if __name__ == "__main__":
    main()
