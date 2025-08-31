#!/usr/bin/env python3
"""
Yabai Setup Verification Script
Checks if all requirements are met and services are running properly
"""

import subprocess
import os
import json

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
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        return e.stderr.strip() if e.stderr else str(e), False

def check_installation():
    """Check if Yabai and SKHD are installed"""
    print("🔍 Checking Installation...")
    
    # Check Yabai
    yabai_path, yabai_ok = run_command("which /opt/homebrew/bin/yabai")
    if yabai_ok and os.path.exists("/opt/homebrew/bin/yabai"):
        print("  ✅ Yabai installed at /opt/homebrew/bin/yabai")
    else:
        print("  ❌ Yabai not found - run: brew install yabai")
        return False
    
    # Check SKHD
    skhd_path, skhd_ok = run_command("which /opt/homebrew/bin/skhd")
    if skhd_ok and os.path.exists("/opt/homebrew/bin/skhd"):
        print("  ✅ SKHD installed at /opt/homebrew/bin/skhd")
    else:
        print("  ❌ SKHD not found - run: brew install skhd")
        return False
    
    return True

def check_configs():
    """Check if configuration files exist"""
    print("\n📁 Checking Configuration Files...")
    
    yabairc_path = os.path.expanduser("~/.yabairc")
    skhdrc_path = os.path.expanduser("~/.skhdrc")
    
    configs_ok = True
    
    if os.path.exists(yabairc_path):
        # Check if executable
        if os.access(yabairc_path, os.X_OK):
            print("  ✅ ~/.yabairc exists and is executable")
        else:
            print("  ⚠️  ~/.yabairc exists but not executable - run: chmod +x ~/.yabairc")
            configs_ok = False
    else:
        print("  ❌ ~/.yabairc not found")
        configs_ok = False
    
    if os.path.exists(skhdrc_path):
        print("  ✅ ~/.skhdrc exists")
    else:
        print("  ❌ ~/.skhdrc not found")
        configs_ok = False
    
    return configs_ok

def check_services():
    """Check if services are running"""
    print("\n🔄 Checking Service Status...")
    
    # Check Yabai service
    yabai_status, _ = run_command("brew services list | grep yabai")
    if "started" in yabai_status:
        print("  ✅ Yabai service is running")
        yabai_running = True
    else:
        print("  ❌ Yabai service not running - run: brew services start yabai")
        yabai_running = False
    
    # Check SKHD service
    skhd_status, _ = run_command("brew services list | grep skhd")
    if "started" in skhd_status:
        print("  ✅ SKHD service is running")
        skhd_running = True
    else:
        print("  ❌ SKHD service not running - run: brew services start skhd")
        skhd_running = False
    
    return yabai_running and skhd_running

def check_yabai_functionality():
    """Test if Yabai is actually working"""
    print("\n🖥️  Testing Yabai Functionality...")
    
    # Try to query spaces
    spaces_result, spaces_ok = run_command("/opt/homebrew/bin/yabai -m query --spaces")
    if spaces_ok:
        try:
            spaces = json.loads(spaces_result)
            print(f"  ✅ Yabai responding - found {len(spaces)} spaces")
            return True
        except json.JSONDecodeError:
            print("  ❌ Yabai responding but output malformed")
            return False
    else:
        print("  ❌ Yabai not responding - check permissions and service status")
        print(f"     Error: {spaces_result}")
        return False

def check_permissions():
    """Check accessibility permissions (basic check)"""
    print("\n🔐 Permission Status...")
    print("  ⚠️  Accessibility permissions cannot be checked programmatically")
    print("     You must manually verify in System Settings:")
    print("     • System Settings → Privacy & Security → Accessibility")
    print("     • Add: /opt/homebrew/bin/yabai")
    print("     • Add: /opt/homebrew/bin/skhd")
    print("     • Add: Terminal (or your terminal app)")
    print("\n  ⚠️  Input Monitoring permissions (for SKHD hotkeys):")
    print("     • System Settings → Privacy & Security → Input Monitoring")  
    print("     • Add: /opt/homebrew/bin/skhd")

def provide_recommendations():
    """Provide setup recommendations"""
    print("\n💡 Setup Recommendations:")
    print("\n1. If services aren't running:")
    print("   brew services start yabai")
    print("   brew services start skhd")
    
    print("\n2. If Yabai isn't responding:")
    print("   • Enable Accessibility permissions (see above)")
    print("   • Restart Yabai: brew services restart yabai")
    
    print("\n3. If hotkeys aren't working:")
    print("   • Enable Input Monitoring for SKHD (see above)")
    print("   • Test: press Alt + 1 to switch to desktop 1")
    
    print("\n4. Test basic functionality:")
    print("   • Open multiple apps")
    print("   • Try Alt + H/J/K/L to focus different windows")
    print("   • Try Alt + F to toggle fullscreen")
    
    print("\n5. If you need more advanced features:")
    print("   • Consider disabling SIP (see documentation)")
    print("   • This enables window animations and more controls")

def main():
    print("🔧 Yabai Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Run all checks
    if not check_installation():
        all_good = False
    
    if not check_configs():
        all_good = False
    
    if not check_services():
        all_good = False
    
    if not check_yabai_functionality():
        all_good = False
    
    check_permissions()
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 Setup looks good! Yabai should be working.")
        print("\n🚀 Quick Test:")
        print("   • Press Alt + 1 to switch to desktop 1")
        print("   • Open a few apps and try Alt + H/J/K/L to focus windows")
        print("   • Try Alt + F to toggle fullscreen on current window")
    else:
        print("⚠️  Some issues found. See recommendations below.")
        provide_recommendations()
    
    print("\n📚 Full documentation available in the setup guide!")
    print("🔍 Run the complete mapper to see current state:")
    print("   python3 complete_mapper.py")

if __name__ == "__main__":
    main()
