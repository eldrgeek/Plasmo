"""
Native automation tools for browser and application automation.

This module contains native automation tools that were factored out from the main
MCP server to reduce complexity and provide specialized automation functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.
"""

import sys
import os
import time
from typing import Dict, Any


def inject_prompt_native(
    prompt: str,
    browser: str = "Chrome",
    use_tab_navigation: bool = True,
    use_clipboard: bool = True,
    typing_delay: float = 0.05,
    delay_between_steps: float = 1.0
) -> Dict[str, Any]:
    """
    Inject prompt into any web browser AI interface using native keyboard automation.
    
    This bypasses JavaScript validation and appears as genuine user input to the browser.
    Works with Gemini, ChatGPT, Claude.ai, or any web-based AI interface.
    
    Args:
        prompt: Text prompt to inject
        browser: Browser name to focus ('Chrome', 'Safari', 'Firefox', 'Edge')
        use_tab_navigation: Whether to use Tab key to navigate to input field
        use_clipboard: If True, use copy/paste instead of typing (much faster)
        typing_delay: Delay between keystrokes in seconds (0 for instant, 0.05 for human-like)
        delay_between_steps: Delay between major automation steps
        
    Returns:
        Dictionary with injection status and detailed step results
    """
    try:
        # Import the native injector
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from gemini_native_injector import GeminiNativeInjector
        
        # Create injector instance
        injector = GeminiNativeInjector()
        
        # Execute the injection
        result = injector.inject_gemini_prompt(
            prompt=prompt,
            browser=browser,
            use_tab_navigation=use_tab_navigation,
            use_clipboard=use_clipboard,
            typing_delay=typing_delay,
            delay_between_steps=delay_between_steps
        )
        
        return result
        
    except ImportError as e:
        return {
            "success": False,
            "error": f"Failed to import native injector: {str(e)}",
            "details": "Ensure gemini_native_injector.py is in the same directory"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Native injection failed: {str(e)}",
            "error_type": type(e).__name__
        }


def focus_and_type_native(
    text: str,
    app_name: str = "Chrome",
    typing_delay: float = 0.05
) -> Dict[str, Any]:
    """
    Focus an application and type text using native automation.
    
    Useful for injecting text into any application, not just browsers.
    
    Args:
        text: Text to type
        app_name: Application name to focus
        typing_delay: Delay between keystrokes (0 for instant)
        
    Returns:
        Dictionary with automation status
    """
    try:
        from gemini_native_injector import GeminiNativeInjector
        
        injector = GeminiNativeInjector()
        
        result = {
            'success': False,
            'steps': [],
            'error': None,
            'app_name': app_name,
            'text_length': len(text)
        }
        
        # Focus the application
        if app_name.lower() in ['chrome', 'safari', 'firefox', 'edge']:
            success, message = injector.focus_browser(app_name)
        else:
            # For non-browser apps, try generic focus (this would need platform-specific implementation)
            success, message = False, f"Generic app focus not implemented for {app_name}"
        
        result['steps'].append({'step': 'focus_app', 'success': success, 'message': message})
        
        if not success:
            result['error'] = f"Failed to focus {app_name}: {message}"
            return result
        
        # Type the text
        time.sleep(0.5)  # Small delay after focusing
        success, message = injector.type_text(text, typing_delay)
        result['steps'].append({'step': 'type_text', 'success': success, 'message': message})
        
        if success:
            result['success'] = True
        else:
            result['error'] = f"Failed to type text: {message}"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Focus and type failed: {str(e)}",
            "error_type": type(e).__name__
        }
