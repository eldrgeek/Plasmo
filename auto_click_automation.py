#!/usr/bin/env python3
"""
Auto-click automation using Chrome Debug Protocol
Automatically clicks the Input Prompt button 1 second after extension reload
"""

import time
import json
import asyncio
from typing import Dict, Any, Optional
import mcp_server

class AutoClickAutomation:
    def __init__(self):
        self.connection_id = "localhost:9222"
        self.bolt_tab_id = None
        self.monitoring = False
        
    def connect_to_chrome(self) -> bool:
        """Connect to Chrome debug protocol"""
        print("🔌 Connecting to Chrome...")
        result = mcp_server.connect_to_chrome()
        if result.get("success"):
            print("✅ Connected to Chrome successfully")
            return True
        else:
            print(f"❌ Failed to connect to Chrome: {result.get('error', 'Unknown error')}")
            return False
    
    def find_bolt_tab(self) -> Optional[str]:
        """Find the bolt.new tab"""
        print("🔍 Looking for bolt.new tab...")
        tabs_result = mcp_server.get_chrome_tabs(self.connection_id)
        
        if not tabs_result.get("success"):
            print(f"❌ Failed to get tabs: {tabs_result.get('error')}")
            return None
        
        tabs = tabs_result.get("tabs", [])
        for tab in tabs:
            if "bolt.new" in tab.get("url", ""):
                tab_id = tab.get("id")
                print(f"✅ Found bolt.new tab: {tab_id}")
                return tab_id
        
        print("❌ No bolt.new tab found")
        return None
    
    def click_input_prompt_button(self, tab_id: str) -> bool:
        """Click the Input Prompt button using JavaScript"""
        print("🖱️ Clicking Input Prompt button...")
        
        # JavaScript to find and click the Input Prompt button
        js_code = """
        (function() {
            // Find the automation container
            const container = document.getElementById("plasmo-bolt-automation");
            if (!container) {
                return {success: false, error: "Automation UI not found"};
            }
            
            // Find the Input Prompt button (first button with 📝 emoji)
            const buttons = container.querySelectorAll("button");
            let inputBtn = null;
            
            for (const btn of buttons) {
                if (btn.textContent && btn.textContent.includes("📝")) {
                    inputBtn = btn;
                    break;
                }
            }
            
            if (!inputBtn) {
                return {success: false, error: "Input Prompt button not found"};
            }
            
            // Check if button is not disabled
            if (inputBtn.disabled) {
                return {success: false, error: "Input Prompt button is disabled"};
            }
            
            // Click the button
            inputBtn.click();
            
            return {
                success: true, 
                message: "Input Prompt button clicked successfully",
                buttonText: inputBtn.textContent
            };
        })();
        """
        
        result = mcp_server.execute_javascript_fixed(js_code, tab_id, self.connection_id)
        
        if result.get("success"):
            js_result = result.get("value", {})
            if js_result.get("success"):
                print(f"✅ {js_result.get('message')}")
                return True
            else:
                print(f"❌ JavaScript execution failed: {js_result.get('error')}")
                return False
        else:
            print(f"❌ Failed to execute JavaScript: {result.get('error')}")
            return False
    
    def wait_for_extension_and_click(self, tab_id: str):
        """Wait for extension to load and then click the button"""
        print("⏳ Waiting 1 second for extension to fully load...")
        time.sleep(1)
        
        # Check if the automation UI is present
        check_ui_js = """
        document.getElementById("plasmo-bolt-automation") !== null
        """
        
        result = mcp_server.execute_javascript_fixed(check_ui_js, tab_id, self.connection_id)
        
        if result.get("success") and result.get("value"):
            print("✅ Automation UI detected")
            return self.click_input_prompt_button(tab_id)
        else:
            print("❌ Automation UI not ready yet")
            return False
    
    def monitor_and_auto_click(self):
        """Monitor for extension reloads and auto-click"""
        if not self.connect_to_chrome():
            return False
        
        tab_id = self.find_bolt_tab()
        if not tab_id:
            print("❌ Please open bolt.new in a Chrome tab first")
            return False
        
        self.bolt_tab_id = tab_id
        self.monitoring = True
        
        print("🚀 Starting auto-click monitoring...")
        print("💡 Reload your extension or refresh the bolt.new page to trigger auto-click")
        print("🛑 Press Ctrl+C to stop monitoring")
        
        try:
            while self.monitoring:
                # Check if page is ready and has our automation UI
                success = self.wait_for_extension_and_click(tab_id)
                if success:
                    print("🎉 Auto-click completed successfully!")
                    print("⏳ Monitoring for next reload...")
                
                # Wait before checking again
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitoring = False
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            self.monitoring = False
    
    def single_click_now(self):
        """Perform a single click right now (for testing)"""
        if not self.connect_to_chrome():
            return False
        
        tab_id = self.find_bolt_tab()
        if not tab_id:
            print("❌ Please open bolt.new in a Chrome tab first")
            return False
        
        print("🎯 Performing single click test...")
        return self.click_input_prompt_button(tab_id)

def main():
    automation = AutoClickAutomation()
    
    print("🤖 Bolt.new Auto-Click Automation")
    print("=" * 40)
    print("1. single - Perform single click test")
    print("2. monitor - Monitor for extension reloads and auto-click")
    
    choice = input("\nChoose mode (1/2): ").strip()
    
    if choice == "1":
        automation.single_click_now()
    elif choice == "2":
        automation.monitor_and_auto_click()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 