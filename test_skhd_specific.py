#!/usr/bin/env python3
"""
SKHD Specific Test
Tests if SKHD is capturing keyboard events and processing config
"""

import subprocess
import time
import os
import signal

def check_skhd_config():
    """Check SKHD configuration file"""
    print("📁 Checking SKHD Configuration...")
    
    config_path = os.path.expanduser("~/.skhdrc")
    if not os.path.exists(config_path):
        print("   ❌ ~/.skhdrc not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            
        # Count configuration lines
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        hotkey_lines = [line for line in lines if ':' in line and 'yabai' in line]
        
        print(f"   ✅ Config file exists ({len(lines)} active lines)")
        print(f"   ✅ Found {len(hotkey_lines)} yabai hotkey bindings")
        
        # Show a few sample bindings
        print("   Sample bindings:")
        for line in hotkey_lines[:3]:
            print(f"     {line}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        return False

def test_skhd_process():
    """Test SKHD process and permissions"""
    print("\n🔍 Checking SKHD Process...")
    
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            check=True
        )
        
        skhd_lines = [line for line in result.stdout.split('\n') if '/opt/homebrew/bin/skhd' in line and 'grep' not in line]
        
        if skhd_lines:
            print("   ✅ SKHD is running:")
            for line in skhd_lines:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"     PID: {pid}")
            return True
        else:
            print("   ❌ SKHD process not found")
            return False
            
    except subprocess.CalledProcessError:
        print("   ❌ Could not check processes")
        return False

def test_skhd_reload():
    """Test SKHD configuration reload"""
    print("\n🔄 Testing SKHD Reload...")
    
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/skhd", "--reload"],
            capture_output=True,
            text=True,
            check=True
        )
        print("   ✅ SKHD reload successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ SKHD reload failed: {e.stderr or str(e)}")
        return False

def create_minimal_test_config():
    """Create a minimal test config to isolate issues"""
    print("\n🧪 Creating Minimal Test Config...")
    
    test_config = """# Minimal SKHD test configuration
# Test if SKHD can capture basic keystrokes

# Simple test: Alt + T should toggle float (less likely to conflict)
alt - t : /opt/homebrew/bin/yabai -m window --toggle float

# Another test: Alt + R should rotate
alt - r : /opt/homebrew/bin/yabai -m space --rotate 90

# Desktop switching (might need scripting addition)
alt - 1 : /opt/homebrew/bin/yabai -m space --focus 1
alt - 2 : /opt/homebrew/bin/yabai -m space --focus 2
"""
    
    backup_path = os.path.expanduser("~/.skhdrc.backup")
    config_path = os.path.expanduser("~/.skhdrc")
    test_path = os.path.expanduser("~/.skhdrc.test")
    
    try:
        # Backup current config
        if os.path.exists(config_path):
            subprocess.run(["cp", config_path, backup_path], check=True)
            print(f"   ✅ Backed up current config to ~/.skhdrc.backup")
        
        # Write minimal test config
        with open(test_path, 'w') as f:
            f.write(test_config)
        
        print(f"   ✅ Created minimal test config at ~/.skhdrc.test")
        print(f"\n   To test with minimal config:")
        print(f"     mv ~/.skhdrc.test ~/.skhdrc")
        print(f"     /opt/homebrew/bin/skhd --reload")
        print(f"     Test: Option ⌥ + T (should toggle window float)")
        print(f"     Test: Option ⌥ + R (should rotate windows)")
        print(f"\n   To restore original config:")
        print(f"     mv ~/.skhdrc.backup ~/.skhdrc")
        print(f"     /opt/homebrew/bin/skhd --reload")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating test config: {e}")
        return False

def check_macos_conflicts():
    """Check for potential macOS shortcut conflicts"""
    print("\n⚠️  Checking for Potential Conflicts...")
    
    print("   Common macOS shortcuts that might conflict:")
    print("   • Option ⌥ + 1-9: Sometimes used by apps for menu items")
    print("   • Mission Control shortcuts might interfere")
    print("   • App-specific shortcuts can override SKHD")
    
    print("\n   To check for conflicts:")
    print("   • System Settings → Keyboard → Shortcuts")
    print("   • Look for Mission Control, App Shortcuts")
    print("   • Try SKHD shortcuts that are less likely to conflict")
    
    print("\n   Less conflicting test shortcuts:")
    print("   • Option ⌥ + T (toggle float)")
    print("   • Option ⌥ + R (rotate)")
    print("   • Shift + Option ⌥ + H (move window)")

def main():
    print("🔧 SKHD Specific Test")
    print("Testing if SKHD can capture and process keyboard events")
    print("=" * 60)
    
    config_ok = check_skhd_config()
    process_ok = test_skhd_process()
    
    if config_ok and process_ok:
        reload_ok = test_skhd_reload()
        
        print(f"\n📊 SKHD Status Summary:")
        print(f"   Config file: {'✅' if config_ok else '❌'}")
        print(f"   Process running: {'✅' if process_ok else '❌'}")
        print(f"   Reload works: {'✅' if reload_ok else '❌'}")
        
        if config_ok and process_ok and reload_ok:
            print(f"\n🧪 SKHD appears to be working correctly!")
            print(f"   If hotkeys still don't work, try these tests:")
            print(f"   • Option ⌥ + T (toggle float - should work)")
            print(f"   • Option ⌥ + R (rotate - should work)")
            print(f"   • Check for macOS shortcut conflicts")
            
            check_macos_conflicts()
            create_minimal_test_config()
        else:
            print(f"\n❌ SKHD has issues that need fixing")
    else:
        print(f"\n❌ SKHD basic setup has problems")
        if not process_ok:
            print("   Try: /opt/homebrew/bin/skhd --start-service")

if __name__ == "__main__":
    main()
