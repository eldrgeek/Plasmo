#!/usr/bin/env python3
"""
Simple auto-click script - monitors for extension reload and clicks Input Prompt button
Usage: python3 auto_click_simple.py
"""

import time
import mcp_server

def auto_click_input_button():
    """Main function to auto-click the input button"""
    
    # Connect to Chrome
    print("🔌 Connecting to Chrome...")
    connection_result = mcp_server.connect_to_chrome()
    if not connection_result.get("success"):
        print(f"❌ Failed to connect to Chrome: {connection_result.get('error')}")
        print("💡 Make sure Chrome is running with debug port: ./launch-chrome-debug.sh")
        return False
    
    print("✅ Connected to Chrome")
    
    # Find bolt.new tab
    print("🔍 Looking for bolt.new tab...")
    tabs_result = mcp_server.get_chrome_tabs()
    if not tabs_result.get("success"):
        print(f"❌ Failed to get tabs: {tabs_result.get('error')}")
        return False
    
    bolt_tab_id = None
    for tab in tabs_result.get("tabs", []):
        if "bolt.new" in tab.get("url", ""):
            bolt_tab_id = tab.get("id")
            break
    
    if not bolt_tab_id:
        print("❌ No bolt.new tab found. Please open bolt.new in Chrome first.")
        return False
    
    print(f"✅ Found bolt.new tab: {bolt_tab_id}")
    
    # Wait 1 second for extension to load
    print("⏳ Waiting 1 second for extension to load...")
    time.sleep(1)
    
    # Click the Input Prompt button
    print("🖱️ Clicking Input Prompt button...")
    
    click_js = """
    (function() {
        const container = document.getElementById("plasmo-bolt-automation");
        if (!container) return {success: false, error: "Automation UI not found"};
        
        const buttons = container.querySelectorAll("button");
        for (const btn of buttons) {
            if (btn.textContent && btn.textContent.includes("📝")) {
                if (btn.disabled) return {success: false, error: "Button is disabled"};
                btn.click();
                return {success: true, message: "Input Prompt button clicked"};
            }
        }
        return {success: false, error: "Input Prompt button not found"};
    })();
    """
    
    result = mcp_server.execute_javascript_fixed(click_js, bolt_tab_id)
    
    if result.get("success"):
        js_result = result.get("value", {})
        if js_result.get("success"):
            print("✅ Input Prompt button clicked successfully!")
            return True
        else:
            print(f"❌ {js_result.get('error')}")
            return False
    else:
        print(f"❌ Failed to execute JavaScript: {result.get('error')}")
        return False

if __name__ == "__main__":
    print("🚀 Auto-clicking Input Prompt button...")
    auto_click_input_button() 