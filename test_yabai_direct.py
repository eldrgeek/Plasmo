#!/usr/bin/env python3
"""
Direct Yabai Functionality Test
Tests Yabai commands directly without SKHD hotkeys
"""

import subprocess
import json
import time

def run_yabai_command(command):
    """Run a yabai command directly"""
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/yabai", "-m"] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr or str(e)}", False

def test_yabai_direct():
    print("🧪 Testing Yabai Direct Commands (No Hotkeys)")
    print("=" * 60)
    
    # Test 1: Query current space
    print("\n1️⃣ Testing space query...")
    spaces_result, spaces_ok = run_yabai_command("query --spaces")
    if spaces_ok:
        try:
            spaces = json.loads(spaces_result)
            current_space = next((s for s in spaces if s.get('has-focus')), None)
            if current_space:
                print(f"   ✅ Currently on space {current_space['index']}")
            else:
                print(f"   ✅ Found {len(spaces)} spaces, but none focused")
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response")
    else:
        print(f"   ❌ {spaces_result}")
        return False
    
    # Test 2: Try to switch spaces directly
    print("\n2️⃣ Testing direct space switching...")
    print("   Attempting to switch to space 2...")
    
    switch_result, switch_ok = run_yabai_command("space --focus 2")
    if switch_ok:
        print("   ✅ Space switch command executed")
        time.sleep(1)
        
        # Verify the switch worked
        verify_result, verify_ok = run_yabai_command("query --spaces")
        if verify_ok:
            try:
                spaces = json.loads(verify_result)
                current_space = next((s for s in spaces if s.get('has-focus')), None)
                if current_space and current_space['index'] == 2:
                    print("   ✅ Successfully switched to space 2!")
                    
                    # Switch back to space 1
                    print("   Switching back to space 1...")
                    run_yabai_command("space --focus 1")
                    time.sleep(1)
                    print("   ✅ Switched back to space 1")
                else:
                    print(f"   ⚠️  Command executed but still on space {current_space['index'] if current_space else 'unknown'}")
            except:
                print("   ❌ Could not verify space switch")
    else:
        print(f"   ❌ Space switch failed: {switch_result}")
    
    # Test 3: Window management
    print("\n3️⃣ Testing window management...")
    windows_result, windows_ok = run_yabai_command("query --windows")
    if windows_ok:
        try:
            windows = json.loads(windows_result)
            managed_windows = [w for w in windows if not w.get('is-floating', True)]
            print(f"   ✅ Found {len(managed_windows)} managed windows")
            
            if managed_windows:
                # Try to focus a different window
                current_window = next((w for w in windows if w.get('has-focus')), None)
                if current_window:
                    print(f"   Current window: {current_window.get('app', 'Unknown')}")
                    
                    # Try to focus next window
                    focus_result, focus_ok = run_yabai_command("window --focus next")
                    if focus_ok:
                        print("   ✅ Window focus command executed")
                    else:
                        print(f"   ⚠️  Window focus failed: {focus_result}")
            else:
                print("   ⚠️  No managed windows to test focus switching")
        except json.JSONDecodeError:
            print("   ❌ Could not parse windows data")
    else:
        print(f"   ❌ {windows_result}")
    
    # Test 4: Configuration check
    print("\n4️⃣ Testing configuration...")
    config_result, config_ok = run_yabai_command("config layout")
    if config_ok:
        print(f"   ✅ Current layout: {config_result}")
    else:
        print(f"   ❌ Could not get config: {config_result}")
    
    return True

def main():
    print("🔧 Direct Yabai Test (Bypassing SKHD)")
    print("This tests if Yabai itself is working properly")
    print("=" * 60)
    
    if test_yabai_direct():
        print("\n✅ Yabai Direct Test Complete!")
        print("\n💡 Results Analysis:")
        print("   • If space switching worked → Yabai is functional")
        print("   • If commands failed → Yabai has permission/config issues")
        print("   • If this works but hotkeys don't → SKHD is the problem")
    else:
        print("\n❌ Yabai has fundamental issues")
        print("   Check accessibility permissions for /opt/homebrew/bin/yabai")

if __name__ == "__main__":
    main()
