#!/usr/bin/env python3
"""
Gemini Native Injector
Uses native keyboard automation to inject prompts into Gemini AI chat interface
Based on cursor_ai_injector.py but adapted for web browser automation
"""

import subprocess
import time
import platform
import logging
import sys
from typing import Optional, Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiNativeInjector:
    """Cross-platform Gemini AI chat automation using native keyboard input"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        logger.info(f"Initializing for platform: {self.platform}")
        
    def _execute_applescript(self, script: str) -> Tuple[bool, str, str]:
        """Execute AppleScript (macOS only)"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def _execute_powershell(self, script: str) -> Tuple[bool, str, str]:
        """Execute PowerShell (Windows only)"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def _execute_xdotool(self, command: str) -> Tuple[bool, str, str]:
        """Execute xdotool (Linux only)"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def copy_to_clipboard(self, text: str) -> Tuple[bool, str]:
        """Copy text to system clipboard"""
        if self.platform == 'darwin':
            try:
                process = subprocess.run(
                    ['pbcopy'],
                    input=text,
                    text=True,
                    capture_output=True,
                    timeout=5
                )
                return process.returncode == 0, "Text copied to clipboard" if process.returncode == 0 else f"Failed to copy: {process.stderr}"
            except Exception as e:
                return False, f"Clipboard copy failed: {str(e)}"
                
        elif self.platform == 'windows':
            script = f'''
            Set-Clipboard -Value @"
{text}
"@
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else "Text copied to clipboard"
            
        elif self.platform == 'linux':
            try:
                # Try xclip first, then xsel as fallback
                for cmd in [['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input']]:
                    try:
                        process = subprocess.run(
                            cmd,
                            input=text,
                            text=True,
                            capture_output=True,
                            timeout=5
                        )
                        if process.returncode == 0:
                            return True, "Text copied to clipboard"
                    except FileNotFoundError:
                        continue
                return False, "Neither xclip nor xsel found - install with: sudo apt-get install xclip"
            except Exception as e:
                return False, f"Clipboard copy failed: {str(e)}"
        
        return False, f"Platform {self.platform} not supported"
    
    def paste_from_clipboard(self) -> Tuple[bool, str]:
        """Paste text from clipboard using native keyboard shortcut"""
        if self.platform == 'darwin':
            script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else "Pasted from clipboard"
            
        elif self.platform == 'windows':
            script = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^v")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else "Pasted from clipboard"
            
        elif self.platform == 'linux':
            success, output, error = self._execute_xdotool("xdotool key ctrl+v")
            return success, error if not success else "Pasted from clipboard"
        
        return False, f"Platform {self.platform} not supported"
    
    def focus_browser(self, browser_name: str = "Chrome") -> Tuple[bool, str]:
        """Focus web browser application"""
        if self.platform == 'darwin':
            # Try different browser names
            browser_apps = {
                "chrome": "Google Chrome",
                "safari": "Safari", 
                "firefox": "Firefox",
                "edge": "Microsoft Edge"
            }
            app_name = browser_apps.get(browser_name.lower(), browser_name)
            
            script = f'''
            tell application "{app_name}"
                activate
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else f"{app_name} focused"
            
        elif self.platform == 'windows':
            script = f'''
            Add-Type -AssemblyName Microsoft.VisualBasic
            [Microsoft.VisualBasic.Interaction]::AppActivate("{browser_name}")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else f"{browser_name} focused"
            
        elif self.platform == 'linux':
            # Try to find and focus browser window
            search_terms = [browser_name.lower(), "chrome", "firefox", "safari"]
            for term in search_terms:
                success, output, error = self._execute_xdotool(f"xdotool search --name {term} windowactivate")
                if success:
                    return True, f"{term} window focused"
            return False, f"Could not find {browser_name} window"
        
        return False, f"Platform {self.platform} not supported"
    
    def send_keyboard_shortcut(self, shortcut: str) -> Tuple[bool, str]:
        """Send keyboard shortcut to focused application"""
        if self.platform == 'darwin':
            # Convert shortcut format (cmd+l -> command down + l)
            keys = shortcut.split('+')
            modifiers = []
            key = keys[-1]
            
            for modifier in keys[:-1]:
                if modifier == 'cmd':
                    modifiers.append('command down')
                elif modifier == 'ctrl':
                    modifiers.append('control down')
                elif modifier == 'alt':
                    modifiers.append('option down')
                elif modifier == 'shift':
                    modifiers.append('shift down')
            
            modifier_str = ' using ' + ' and '.join(modifiers) if modifiers else ''
            
            script = f'''
            tell application "System Events"
                keystroke "{key}"{modifier_str}
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else f"Sent {shortcut}"
            
        elif self.platform == 'windows':
            # Convert to Windows SendKeys format
            key_map = {'cmd': '^', 'ctrl': '^', 'alt': '%', 'shift': '+'}
            converted = shortcut
            for old, new in key_map.items():
                converted = converted.replace(old + '+', new)
            
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{converted}")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else f"Sent {shortcut}"
            
        elif self.platform == 'linux':
            # Convert to xdotool format
            converted = shortcut.replace('cmd', 'ctrl').replace('+', '+')
            success, output, error = self._execute_xdotool(f"xdotool key {converted}")
            return success, error if not success else f"Sent {shortcut}"
        
        return False, f"Platform {self.platform} not supported"
    
    def type_text(self, text: str, typing_delay: float = 0.05) -> Tuple[bool, str]:
        """Type text into focused input with optional typing delay for more human-like input"""
        if self.platform == 'darwin':
            # For more natural typing, we can add delays between characters
            if typing_delay > 0:
                for char in text:
                    escaped_char = char.replace('\\', '\\\\').replace('"', '\\"')
                    script = f'''
                    tell application "System Events"
                        keystroke "{escaped_char}"
                    end tell
                    '''
                    success, output, error = self._execute_applescript(script)
                    if not success:
                        return False, f"Failed to type character: {error}"
                    time.sleep(typing_delay)
                return True, "Text typed with delay"
            else:
                # Escape quotes and backslashes for AppleScript
                escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
                script = f'''
                tell application "System Events"
                    keystroke "{escaped_text}"
                end tell
                '''
                success, output, error = self._execute_applescript(script)
                return success, error if not success else "Text typed"
            
        elif self.platform == 'windows':
            # Escape for PowerShell SendKeys
            escaped_text = text.replace('{', '{{').replace('}', '}}').replace('[', '{{[}}').replace(']', '{{]}}')
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{escaped_text}")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else "Text typed"
            
        elif self.platform == 'linux':
            if typing_delay > 0:
                # Type with delay using xdotool
                success, output, error = self._execute_xdotool(f'xdotool type --delay {int(typing_delay * 1000)} "{text}"')
            else:
                success, output, error = self._execute_xdotool(f'xdotool type "{text}"')
            return success, error if not success else "Text typed"
        
        return False, f"Platform {self.platform} not supported"
    
    def send_enter(self) -> Tuple[bool, str]:
        """Send Enter key"""
        if self.platform == 'darwin':
            script = '''
            tell application "System Events"
                keystroke return
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else "Enter sent"
            
        elif self.platform == 'windows':
            script = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else "Enter sent"
            
        elif self.platform == 'linux':
            success, output, error = self._execute_xdotool("xdotool key Return")
            return success, error if not success else "Enter sent"
        
        return False, f"Platform {self.platform} not supported"
    
    def send_tab(self, count: int = 1) -> Tuple[bool, str]:
        """Send Tab key(s) for navigation"""
        if self.platform == 'darwin':
            script = f'''
            tell application "System Events"
                repeat {count} times
                    keystroke tab
                    delay 0.1
                end repeat
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else f"Sent {count} tab(s)"
            
        elif self.platform == 'windows':
            tabs = "{TAB}" * count
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{tabs}")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else f"Sent {count} tab(s)"
            
        elif self.platform == 'linux':
            for _ in range(count):
                success, output, error = self._execute_xdotool("xdotool key Tab")
                if not success:
                    return False, error
                time.sleep(0.1)
            return True, f"Sent {count} tab(s)"
        
        return False, f"Platform {self.platform} not supported"
    
    def click_at_coordinates(self, x: int, y: int) -> Tuple[bool, str]:
        """Click at specific screen coordinates (useful for focusing input areas)"""
        if self.platform == 'darwin':
            script = f'''
            tell application "System Events"
                click at {{{x}, {y}}}
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else f"Clicked at ({x}, {y})"
            
        elif self.platform == 'windows':
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("{{LBUTTON}}")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else f"Clicked at ({x}, {y})"
            
        elif self.platform == 'linux':
            success, output, error = self._execute_xdotool(f"xdotool mousemove {x} {y} click 1")
            return success, error if not success else f"Clicked at ({x}, {y})"
        
        return False, f"Platform {self.platform} not supported"
    
    def inject_gemini_prompt(self, prompt: str, browser: str = "Chrome", 
                           use_tab_navigation: bool = True, 
                           use_clipboard: bool = True,
                           typing_delay: float = 0.05,
                           delay_between_steps: float = 1.0) -> Dict[str, Any]:
        """
        Inject prompt into Gemini AI interface using native keyboard automation
        
        Args:
            prompt: Text to inject
            browser: Browser name to focus
            use_tab_navigation: If True, use Tab key to navigate to input field
            use_clipboard: If True, use copy/paste instead of typing (much faster)
            typing_delay: Delay between individual keystrokes (0 for instant, ignored if using clipboard)
            delay_between_steps: Delay between major steps
            
        Returns:
            Dict with success status and details
        """
        result = {
            'success': False,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'steps': [],
            'error': None,
            'browser': browser,
            'platform': self.platform,
            'method': 'clipboard' if use_clipboard else 'typing'
        }
        
        try:
            # Step 1: Focus browser
            logger.info(f"Focusing {browser} browser")
            success, message = self.focus_browser(browser)
            result['steps'].append({'step': 'focus_browser', 'success': success, 'message': message})
            if not success:
                result['error'] = f"Failed to focus browser: {message}"
                return result
            
            time.sleep(delay_between_steps)
            
            # Step 2: Navigate to input field (if requested)
            if use_tab_navigation:
                logger.info("Navigating to input field using Tab")
                # Check if the input field is already focused
                if not is_input_field_focused():
                    # Navigate to input field using Tab if not already focused
                    navigate_to_input_field()
                
                time.sleep(delay_between_steps * 0.5)
            
            # Step 3: Input the prompt (clipboard or typing)
            if use_clipboard:
                # Copy to clipboard first
                logger.info(f"Copying prompt to clipboard ({len(prompt)} characters)")
                success, message = self.copy_to_clipboard(prompt)
                result['steps'].append({'step': 'copy_to_clipboard', 'success': success, 'message': message})
                if not success:
                    result['error'] = f"Failed to copy to clipboard: {message}"
                    return result
                
                time.sleep(0.2)  # Small delay after copying
                
                # Paste from clipboard
                logger.info("Pasting prompt from clipboard")
                success, message = self.paste_from_clipboard()
                result['steps'].append({'step': 'paste_prompt', 'success': success, 'message': message})
                if not success:
                    result['error'] = f"Failed to paste from clipboard: {message}"
                    return result
            else:
                # Type the prompt character by character
                logger.info(f"Typing prompt ({len(prompt)} characters)")
                success, message = self.type_text(prompt, typing_delay)
                result['steps'].append({'step': 'type_prompt', 'success': success, 'message': message})
                if not success:
                    result['error'] = f"Failed to type prompt: {message}"
                    return result
            
            time.sleep(delay_between_steps * 0.5)
            
            # Step 4: Send the prompt
            logger.info("Sending prompt with Enter key")
            success, message = self.send_enter()
            result['steps'].append({'step': 'send_prompt', 'success': success, 'message': message})
            if not success:
                result['error'] = f"Failed to send prompt: {message}"
                return result
            
            result['success'] = True
            method_used = "clipboard copy/paste" if use_clipboard else f"typing with {typing_delay}s delay"
            logger.info(f"Gemini prompt injection completed successfully using {method_used}")
            
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.error(f"Gemini prompt injection failed: {e}")
        
        return result

# Define a function to check if the input field is focused
def is_input_field_focused():
    # Logic to determine if the input field is focused
    # This could involve checking the active element in the browser
    return True  # Placeholder, implement actual check

# Define a function to navigate to the input field using Tab
def navigate_to_input_field():
    # Logic to navigate to the input field using Tab
    pass  # Placeholder, implement actual navigation logic

def main():
    """CLI interface for testing Gemini injection"""
    if len(sys.argv) < 2:
        print("Usage: python gemini_native_injector.py 'Your prompt here'")
        print("Optional: python gemini_native_injector.py 'Your prompt' --browser=Chrome --use-clipboard")
        sys.exit(1)
    
    prompt = sys.argv[1]
    browser = "Chrome"
    typing_delay = 0.05
    use_clipboard = False
    
    # Parse optional arguments
    for arg in sys.argv[2:]:
        if arg.startswith('--browser='):
            browser = arg.split('=')[1]
        elif arg.startswith('--typing-delay='):
            typing_delay = float(arg.split('=')[1])
        elif arg == '--use-clipboard':
            use_clipboard = True
    
    print(f"🤖 Gemini Native Injector Experiment")
    print(f"Platform: {platform.system()}")
    print(f"Browser: {browser}")
    print(f"Prompt: {prompt[:50]}...")
    print(f"Method: {'Clipboard (copy/paste)' if use_clipboard else f'Typing (delay: {typing_delay}s)'}")
    print()
    print("⚠️  Make sure Gemini is open in your browser and visible!")
    print("⚠️  You have 5 seconds to focus the browser window...")
    
    for i in range(5, 0, -1):
        print(f"Starting in {i}...", end='\r')
        time.sleep(1)
    print()
    
    injector = GeminiNativeInjector()
    result = injector.inject_gemini_prompt(
        prompt=prompt,
        browser=browser,
        use_clipboard=use_clipboard,
        typing_delay=typing_delay
    )
    
    print("\n📊 Results:")
    print(f"Success: {result['success']}")
    print(f"Method: {result['method']}")
    if result['error']:
        print(f"Error: {result['error']}")
    
    print("\n📋 Steps:")
    for step in result['steps']:
        status = "✅" if step['success'] else "❌"
        print(f"  {status} {step['step']}: {step['message']}")
    
    print(f"\nInjection result: {result}")

if __name__ == "__main__":
    main() 