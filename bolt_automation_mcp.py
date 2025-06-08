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
    
    // Focus the textarea first
    textarea.focus();
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Clear existing content by selecting all and "typing" over it
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);
    
    // Simulate real user typing to clear and enter new content
    // First, simulate Ctrl+A to select all
    textarea.dispatchEvent(new KeyboardEvent('keydown', {{ 
        key: 'a', 
        code: 'KeyA', 
        ctrlKey: true, 
        bubbles: true 
    }}));
    
    // Then simulate typing the new content character by character
    textarea.value = ''; // Clear first
    
    for (let i = 0; i < promptText.length; i++) {{
        const char = promptText[i];
        
        // Simulate keydown
        textarea.dispatchEvent(new KeyboardEvent('keydown', {{
            key: char,
            code: `Key${{char.toUpperCase()}}`,
            bubbles: true
        }}));
        
        // Update value incrementally  
        textarea.value = promptText.substring(0, i + 1);
        
        // Simulate input event (this is what React watches)
        textarea.dispatchEvent(new Event('input', {{ 
            bubbles: true,
            data: char,
            inputType: 'insertText'
        }}));
        
        // Small delay between characters to mimic human typing
        if (i % 10 === 0) {{ // Only delay every 10 chars for speed
            await new Promise(resolve => setTimeout(resolve, 10));
        }}
    }}
    
    // Final events to ensure React state is updated
    textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
    
    // Verify the content is set
    console.log(`📝 Textarea content after typing: "${{textarea.value}}"`);
    
    // Small delay to let React process the state change
    await new Promise(resolve => setTimeout(resolve, 300));
    
    console.log(`✅ Injected prompt: "${{promptText.substring(0, 50)}}..."`);
    
    // Wait a moment for any reactive updates
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Find and click submit button
    const submitSelectors = [
        'button[type="submit"]',
        'button:has(svg)', // Look for button with SVG icon (common in Bolt)
        'button[aria-label*="submit" i]',
        'button[aria-label*="send" i]',
        'button[data-testid*="submit" i]',
        'button[data-testid*="send" i]',
        '.submit-button',
        '.send-button',
        'button.bg-', // Tailwind styled buttons
        'form button', // Button inside form
    ];
    
    const submitTextPatterns = [
        'submit', 'send', 'generate', 'create', 'build', 'go', '→', '▶', '✓'
    ];
    
    let submitButton = null;
    
    console.log('🔍 Looking for submit button...');
    
    // Try specific selectors first
    for (const selector of submitSelectors) {{
        const buttons = document.querySelectorAll(selector);
        console.log(`Trying selector: ${{selector}} - found ${{buttons.length}} elements`);
        
        for (const button of buttons) {{
            if (button && !button.disabled && button.offsetParent !== null) {{ // Check if visible
                submitButton = button;
                console.log(`✅ Found submit button with selector: ${{selector}}`);
                break;
            }}
        }}
        if (submitButton) break;
    }}
    
    // If no specific selector worked, try text-based search
    if (!submitButton) {{
        console.log('🔍 Trying text-based button search...');
        const allButtons = document.querySelectorAll('button');
        console.log(`Found ${{allButtons.length}} total buttons`);
        
        for (const button of allButtons) {{
            const buttonText = button.textContent?.toLowerCase().trim() || '';
            const hasSubmitText = submitTextPatterns.some(pattern => 
                buttonText.includes(pattern.toLowerCase())
            );
            
            console.log(`Button text: "${{buttonText}}" - hasSubmitText: ${{hasSubmitText}} - disabled: ${{button.disabled}} - visible: ${{button.offsetParent !== null}}`);
            
            if (hasSubmitText && !button.disabled && button.offsetParent !== null) {{
                submitButton = button;
                console.log(`✅ Found submit button by text: "${{buttonText}}"`);
                break;
            }}
        }}
    }}
    
    // Last resort: look for any button near the textarea
    if (!submitButton) {{
        console.log('🔍 Looking for any button near textarea...');
        const nearbyButtons = document.querySelectorAll('button');
        for (const button of nearbyButtons) {{
            if (!button.disabled && button.offsetParent !== null) {{
                const rect = button.getBoundingClientRect();
                const textareaRect = textarea.getBoundingClientRect();
                
                // Check if button is reasonably close to textarea
                if (Math.abs(rect.top - textareaRect.bottom) < 100) {{
                    submitButton = button;
                    console.log(`✅ Found nearby button: "${{button.textContent?.trim() || 'no text'}}"`);
                    break;
                }}
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
    
    // Wait a bit and check for any response indicators
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Look for signs that Bolt is processing
    const responseIndicators = [
        '[class*="loading"]',
        '[class*="generating"]',
        '[class*="thinking"]',
        '.prose', // Response content area
        'pre code', // Code blocks
        '[role="article"]'
    ];
    
    let processingDetected = false;
    for (const selector of responseIndicators) {{
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {{
            console.log(`✅ Found response indicator: ${{selector}} (${{elements.length}} elements)`);
            processingDetected = true;
            break;
        }}
    }}
    
    const result = {{ 
        success: true, 
        promptInjected: true, 
        buttonClicked: true,
        processingDetected: processingDetected,
        textareaValue: textarea.value,
        message: 'Automation completed successfully'
    }};
    
    console.log('🎉 Final result:', JSON.stringify(result, null, 2));
    return result;
}})();
"""

    def find_bolt_tab(self, tabs_data: Dict[str, Any]) -> str:
        """Find Bolt.new tab ID from MCP response"""
        if not tabs_data.get("success"):
            return None
            
        tabs = tabs_data.get("tabs", [])
        
        # Look for the actual bolt.new page (not DevTools)
        for tab in tabs:
            title = tab.get("title", "")
            url = tab.get("url", "")
            
            # Must be the actual bolt.new URL, not DevTools
            if "https://bolt.new" in url and "devtools://" not in url:
                print(f"✅ Found Bolt tab: {title} - {url}")
                return tab.get("id")
        
        # Fallback: look for other bolt-related patterns (but not DevTools)
        bolt_patterns = ["stackblitz.com", "bolt.diy"]
        
        for tab in tabs:
            title = tab.get("title", "").lower()
            url = tab.get("url", "").lower()
            
            # Skip DevTools tabs
            if "devtools://" in url:
                continue
                
            for pattern in bolt_patterns:
                if pattern in url or (pattern in title and "devtools" not in title):
                    print(f"✅ Found Bolt-related tab: {tab.get('title')} - {tab.get('url')}")
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