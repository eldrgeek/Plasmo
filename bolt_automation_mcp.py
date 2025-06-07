#!/usr/bin/env python3
"""
Bolt.new automation using MCP server direct function calls
Uses the existing MCP server tools by importing and calling them directly
"""

import asyncio
import json
import sys
from typing import Dict, Any

# Import MCP server functions directly
sys.path.append('.')
import mcp_server

class MCPBoltAutomation:
    def __init__(self):
        self.connection_id = "localhost:9222"
        
    def get_chrome_tabs(self) -> Dict[str, Any]:
        """Get Chrome tabs using MCP server"""
        return mcp_server.get_chrome_tabs(self.connection_id)
    
    def execute_javascript(self, code: str, tab_id: str) -> Dict[str, Any]:
        """Execute JavaScript in Chrome tab using MCP server"""
        return mcp_server.execute_javascript_fixed(code, tab_id, self.connection_id)
    
    def create_injection_script(self, prompt_text: str) -> str:
        """Create JavaScript code to inject prompt and submit"""
        # Escape single quotes in the prompt text
        escaped_prompt = prompt_text.replace("'", "\\'").replace("\\", "\\\\").replace("\n", "\\n")
        
        return f"""
(async function() {{
    console.log('🤖 Starting Bolt.new automation via MCP...');
    
    // Multiple selectors to find textarea
    const textareaSelectors = [
        'textarea[placeholder*="prompt" i]',
        'textarea[placeholder*="describe" i]',
        'textarea[placeholder*="build" i]',
        'textarea[data-testid*="prompt" i]',
        'textarea[aria-label*="prompt" i]',
        'div[contenteditable="true"]',
        'textarea:not([style*="display: none"])',
        '.prompt-input textarea',
        '#prompt-input',
        '[data-cy="prompt-textarea"]',
        'textarea'
    ];
    
    let textarea = null;
    
    // Try each selector
    for (const selector of textareaSelectors) {{
        const elements = document.querySelectorAll(selector);
        for (const element of elements) {{
            const rect = element.getBoundingClientRect();
            const isVisible = rect.width > 0 && rect.height > 0 && 
                            window.getComputedStyle(element).display !== 'none' &&
                            window.getComputedStyle(element).visibility !== 'hidden';
            
            if (isVisible) {{
                textarea = element;
                console.log(`✅ Found textarea with selector: ${{selector}}`);
                break;
            }}
        }}
        if (textarea) break;
    }}
    
    if (!textarea) {{
        console.error('❌ No suitable textarea found');
        return {{ success: false, error: 'No textarea found' }};
    }}
    
    // Inject the prompt
    const promptText = '{escaped_prompt}';
    
    // Clear existing content and inject new prompt
    textarea.focus();
    textarea.value = '';
    
    // Use multiple methods to set the value
    textarea.value = promptText;
    textarea.textContent = promptText;
    
    // Trigger input events
    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
    textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
    
    console.log(`✅ Injected prompt: "${{promptText.substring(0, 50)}}..."`);
    
    // Wait a moment for any reactive updates
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Find and click submit button
    const submitSelectors = [
        'button[type="submit"]',
        'button:has(svg)',
        'button[aria-label*="submit" i]',
        'button[aria-label*="send" i]',
        'button[data-testid*="submit" i]',
        'button[data-testid*="send" i]',
        '.submit-button',
        '.send-button'
    ];
    
    const submitTextPatterns = [
        'submit', 'send', 'generate', 'create', 'build', 'go', '→', '▶'
    ];
    
    let submitButton = null;
    
    // Try specific selectors first
    for (const selector of submitSelectors) {{
        const button = document.querySelector(selector);
        if (button && !button.disabled) {{
            submitButton = button;
            console.log(`✅ Found submit button with selector: ${{selector}}`);
            break;
        }}
    }}
    
    // If no specific selector worked, try text-based search
    if (!submitButton) {{
        const allButtons = document.querySelectorAll('button');
        for (const button of allButtons) {{
            const buttonText = button.textContent?.toLowerCase().trim() || '';
            const hasSubmitText = submitTextPatterns.some(pattern => 
                buttonText.includes(pattern.toLowerCase())
            );
            
            if (hasSubmitText && !button.disabled) {{
                submitButton = button;
                console.log(`✅ Found submit button by text: "${{buttonText}}"`);
                break;
            }}
        }}
    }}
    
    if (!submitButton) {{
        console.error('❌ No submit button found');
        return {{ 
            success: false, 
            error: 'No submit button found',
            promptInjected: true
        }};
    }}
    
    // Click the submit button
    submitButton.click();
    console.log('✅ Clicked submit button');
    
    return {{ 
        success: true, 
        promptInjected: true, 
        buttonClicked: true,
        message: 'Automation completed successfully'
    }};
}})();
"""

    def find_bolt_tab(self, tabs_data: Dict[str, Any]) -> str:
        """Find Bolt.new tab ID from MCP response"""
        if not tabs_data.get("success"):
            return None
            
        tabs = tabs_data.get("tabs", [])
        
        bolt_patterns = [
            "bolt.new",
            "bolt.diy", 
            "stackblitz.com",
            "Bolt"
        ]
        
        for tab in tabs:
            title = tab.get("title", "").lower()
            url = tab.get("url", "").lower()
            
            for pattern in bolt_patterns:
                if pattern.lower() in url or pattern.lower() in title:
                    print(f"✅ Found Bolt tab: {tab.get('title')} - {tab.get('url')}")
                    return tab.get("id")
        
        return None
    
    def automate_bolt(self, prompt: str) -> Dict[str, Any]:
        """Main automation function"""
        print(f"🎯 Prompt to inject: {prompt}")
        print("🚀 Starting Bolt.new automation via MCP server...")
        
        # Step 1: Connect to Chrome
        connection_result = mcp_server.connect_to_chrome()
        if not connection_result.get("success"):
            return {"success": False, "error": f"Could not connect to Chrome: {connection_result.get('error')}"}
        
        # Step 2: Get Chrome tabs
        tabs_result = self.get_chrome_tabs()
        print(f"📋 Chrome tabs result: {json.dumps(tabs_result, indent=2)}")
        
        if not tabs_result.get("success"):
            return {"success": False, "error": f"Could not get Chrome tabs: {tabs_result.get('error')}"}
        
        # Step 3: Find Bolt.new tab
        bolt_tab_id = self.find_bolt_tab(tabs_result)
        
        if not bolt_tab_id:
            available_tabs = [f"{tab.get('title', 'No title')} - {tab.get('url', 'No URL')}" 
                            for tab in tabs_result.get("tabs", [])]
            return {
                "success": False,
                "error": "No Bolt.new tab found",
                "available_tabs": available_tabs
            }
        
        print(f"🎯 Using Bolt tab ID: {bolt_tab_id}")
        
        # Step 4: Create and execute JavaScript
        js_code = self.create_injection_script(prompt)
        execution_result = self.execute_javascript(js_code, bolt_tab_id)
        
        print(f"📜 JavaScript execution result: {json.dumps(execution_result, indent=2)}")
        
        if execution_result.get("success"):
            result_value = execution_result.get("result", {})
            if isinstance(result_value, dict) and result_value.get("success"):
                return {
                    "success": True,
                    "tab_id": bolt_tab_id,
                    "automation_result": result_value,
                    "message": "Bolt.new automation completed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"JavaScript execution succeeded but automation failed: {result_value}",
                    "tab_id": bolt_tab_id
                }
        else:
            return {
                "success": False,
                "error": f"JavaScript execution failed: {execution_result.get('error')}",
                "tab_id": bolt_tab_id
            }

def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print("Usage: python bolt_automation_mcp.py '<prompt>'")
        print("Example: python bolt_automation_mcp.py 'Create a simple React todo app'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    automator = MCPBoltAutomation()
    result = automator.automate_bolt(prompt)
    
    print("\n" + "="*50)
    print("🏁 AUTOMATION RESULT:")
    print("="*50)
    print(json.dumps(result, indent=2))
    
    if result.get("success"):
        print("✅ Automation completed successfully!")
    else:
        print("❌ Automation failed:")
        print(f"Error: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 