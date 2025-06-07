#!/usr/bin/env python3
"""
Cursor AI Chat Injector
Provides keyboard automation to inject prompts into Cursor's AI chat interface
Compatible with macOS, Windows, and Linux
"""

import subprocess
import time
import platform
import logging
from typing import Optional, Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CursorAIInjector:
    """Cross-platform Cursor AI chat automation"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.shortcuts = self._get_platform_shortcuts()
        
    def _get_platform_shortcuts(self) -> Dict[str, str]:
        """Get platform-specific keyboard shortcuts"""
        shortcuts = {
            'darwin': {  # macOS
                'chat': 'cmd+l',
                'composer': 'cmd+i',
                'inline_edit': 'cmd+k'
            },
            'windows': {  # Windows
                'chat': 'ctrl+l',
                'composer': 'ctrl+i', 
                'inline_edit': 'ctrl+k'
            },
            'linux': {  # Linux
                'chat': 'ctrl+l',
                'composer': 'ctrl+i',
                'inline_edit': 'ctrl+k'
            }
        }
        return shortcuts.get(self.platform, shortcuts['linux'])
    
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
    
    def focus_cursor(self) -> Tuple[bool, str]:
        """Focus Cursor application"""
        if self.platform == 'darwin':
            script = '''
            tell application "Cursor"
                activate
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success, error if not success else "Cursor focused"
            
        elif self.platform == 'windows':
            script = '''
            Add-Type -AssemblyName Microsoft.VisualBasic
            [Microsoft.VisualBasic.Interaction]::AppActivate("Cursor")
            '''
            success, output, error = self._execute_powershell(script)
            return success, error if not success else "Cursor focused"
            
        elif self.platform == 'linux':
            # Try to find and focus Cursor window
            success, output, error = self._execute_xdotool("xdotool search --name Cursor windowactivate")
            return success, error if not success else "Cursor focused"
        
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
    
    def type_text(self, text: str) -> Tuple[bool, str]:
        """Type text into focused input"""
        if self.platform == 'darwin':
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
    
    def is_chat_panel_focused(self) -> Tuple[bool, str]:
        """
        Attempt to detect if Cursor's chat panel is already focused
        This is a best-effort detection using UI elements
        """
        if self.platform == 'darwin':
            # Try to detect if chat input is already focused
            script = '''
            tell application "System Events"
                tell process "Cursor"
                    try
                        -- Look for text input fields that might be the chat input
                        set inputFields to text fields whose value is ""
                        if (count of inputFields) > 0 then
                            return "likely_focused"
                        end if
                        
                        -- Check if there's a focused text area
                        set textAreas to text areas whose focused is true
                        if (count of textAreas) > 0 then
                            return "likely_focused"
                        end if
                        
                        return "unknown"
                    on error
                        return "unknown"
                    end try
                end tell
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            is_focused = output.strip() == "likely_focused"
            return is_focused, "Chat panel focus detected" if is_focused else "Cannot determine chat panel state"
            
        elif self.platform == 'windows':
            # Windows detection is more limited, return unknown
            return False, "Chat panel detection not available on Windows"
            
        elif self.platform == 'linux':
            # Linux detection using window properties
            success, output, error = self._execute_xdotool("xdotool getwindowfocus getwindowname")
            if success and "cursor" in output.lower():
                return False, "Chat panel detection limited on Linux"
            return False, "Cannot determine chat panel state"
        
        return False, f"Platform {self.platform} not supported"
    
    def inject_prompt(self, prompt: str, mode: str = 'chat', delay: float = 0.5, 
                     assume_focused: bool = False, skip_toggle: bool = False,
                     completion_detection: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Inject prompt into Cursor AI interface with optional completion detection
        
        Args:
            prompt: Text to inject
            mode: 'chat', 'composer', or 'inline_edit'
            delay: Delay between actions in seconds
            assume_focused: If True, assume the chat panel is already focused (skip toggle)
            skip_toggle: If True, never send the keyboard shortcut to toggle the panel
            completion_detection: Dict with completion detection options:
                {
                    "enabled": bool,
                    "methods": ["file", "http", "both"],
                    "file_path": str,
                    "http_endpoint": str,
                    "completion_id": str,
                    "include_results": bool,
                    "auto_append": bool
                }
            
        Returns:
            Dict with success status and details
        """
        result = {
            'success': False,
            'mode': mode,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'steps': [],
            'error': None,
            'panel_detection': None,
            'completion_detection': completion_detection or {}
        }
        
        # Process completion detection options
        enhanced_prompt = self._prepare_prompt_with_completion(prompt, completion_detection)
        
        try:
            # Step 1: Focus Cursor
            logger.info("Focusing Cursor application")
            success, message = self.focus_cursor()
            result['steps'].append({'step': 'focus', 'success': success, 'message': message})
            if not success:
                result['error'] = f"Failed to focus Cursor: {message}"
                return result
            
            time.sleep(delay)
            
            # Step 2: Determine if we need to toggle the panel
            should_toggle = True
            
            if assume_focused:
                should_toggle = False
                result['panel_detection'] = "assumed_focused"
                logger.info("Assuming chat panel is already focused (skip_toggle=True)")
            elif skip_toggle:
                should_toggle = False
                result['panel_detection'] = "skip_requested"
                logger.info("Skipping panel toggle as requested")
            else:
                # Try to detect if panel is already focused
                is_focused, detection_msg = self.is_chat_panel_focused()
                result['panel_detection'] = detection_msg
                
                if is_focused:
                    should_toggle = False
                    logger.info(f"Chat panel appears to be focused: {detection_msg}")
                else:
                    logger.info(f"Will toggle panel: {detection_msg}")
            
            # Step 2b: Toggle panel if needed
            if should_toggle:
                shortcut = self.shortcuts.get(mode, self.shortcuts['chat'])
                logger.info(f"Opening {mode} mode with {shortcut}")
                success, message = self.send_keyboard_shortcut(shortcut)
                result['steps'].append({'step': 'open_mode', 'success': success, 'message': message})
                if not success:
                    result['error'] = f"Failed to open {mode}: {message}"
                    return result
                
                time.sleep(delay * 2)  # Longer delay for interface to open
            else:
                result['steps'].append({'step': 'open_mode', 'success': True, 'message': 'Skipped - panel assumed focused'})
                time.sleep(delay * 0.5)  # Shorter delay since no UI change
            
            # Step 3: Type the enhanced prompt (with completion instructions if enabled)
            logger.info(f"Typing prompt ({len(enhanced_prompt)} characters)")
            success, message = self.type_text(enhanced_prompt)
            result['steps'].append({'step': 'type_prompt', 'success': success, 'message': message})
            if not success:
                result['error'] = f"Failed to type prompt: {message}"
                return result
            
            time.sleep(delay)
            
            # Step 4: Send the prompt
            logger.info("Sending prompt")
            success, message = self.send_enter()
            result['steps'].append({'step': 'send_prompt', 'success': success, 'message': message})
            if not success:
                result['error'] = f"Failed to send prompt: {message}"
                return result
            
            # Step 5: Setup completion monitoring if enabled
            if completion_detection and completion_detection.get('enabled'):
                self._setup_completion_monitoring(completion_detection, result)
            
            result['success'] = True
            logger.info("Prompt injection completed successfully")
            
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.error(f"Prompt injection failed: {e}")
        
        return result
    
    def _prepare_prompt_with_completion(self, original_prompt: str, completion_config: Dict[str, Any] = None) -> str:
        """Prepare prompt with completion detection instructions if enabled"""
        if not completion_config or not completion_config.get('enabled'):
            return original_prompt
        
        if not completion_config.get('auto_append', True):
            return original_prompt
        
        methods = completion_config.get('methods', ['file'])
        completion_id = completion_config.get('completion_id', f"completion_{int(time.time())}")
        include_results = completion_config.get('include_results', False)
        
        # Build completion instructions
        instructions = [
            "\n\n---",
            "IMPORTANT: When you have finished responding completely, please perform the following actions to signal completion:"
        ]
        
        if 'file' in methods or 'both' in methods:
            file_path = completion_config.get('file_path', '/tmp/cursor_ai_completion.json')
            if include_results:
                instructions.append(f"1. Write a JSON file to: {file_path}")
                instructions.append(f"   Content: {{\"completion_id\": \"{completion_id}\", \"status\": \"completed\", \"timestamp\": \"<current_timestamp>\", \"summary\": \"<brief_summary_of_your_response>\"}}")
            else:
                instructions.append(f"1. Write the text 'COMPLETED:{completion_id}' to: {file_path}")
        
        if 'http' in methods or 'both' in methods:
            endpoint = completion_config.get('http_endpoint', 'http://localhost:3001/api/ai-completion')
            if include_results:
                instructions.append(f"2. Make a POST request to: {endpoint}")
                instructions.append(f"   Body: {{\"completion_id\": \"{completion_id}\", \"status\": \"completed\", \"timestamp\": \"<current_timestamp>\", \"summary\": \"<brief_summary_of_your_response>\"}}")
            else:
                instructions.append(f"2. Make a POST request to: {endpoint}")
                instructions.append(f"   Body: {{\"completion_id\": \"{completion_id}\", \"status\": \"completed\"}}")
        
        instructions.extend([
            "",
            "Please perform these actions immediately after your response is complete.",
            "---"
        ])
        
        return original_prompt + "\n".join(instructions)
    
    def _setup_completion_monitoring(self, completion_config: Dict[str, Any], result: Dict[str, Any]):
        """Setup monitoring for completion signals"""
        methods = completion_config.get('methods', ['file'])
        completion_id = completion_config.get('completion_id', f"completion_{int(time.time())}")
        
        monitoring_info = {
            'completion_id': completion_id,
            'methods': methods,
            'monitoring_started': time.time()
        }
        
        if 'file' in methods or 'both' in methods:
            file_path = completion_config.get('file_path', '/tmp/cursor_ai_completion.json')
            monitoring_info['file_path'] = file_path
            # Clear any existing completion file
            try:
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not clear completion file: {e}")
        
        result['completion_monitoring'] = monitoring_info
        logger.info(f"Completion monitoring setup: {monitoring_info}")

    def wait_for_completion(self, completion_config: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """
        Wait for AI completion signal
        
        Args:
            completion_config: Completion detection configuration
            timeout: Maximum time to wait in seconds
            
        Returns:
            Dict with completion status and details
        """
        import os
        import time
        import json
        from pathlib import Path
        
        result = {
            'completed': False,
            'method': None,
            'completion_time': None,
            'timeout': False,
            'error': None,
            'data': None
        }
        
        completion_id = completion_config.get('completion_id')
        methods = completion_config.get('methods', ['file'])
        file_path = completion_config.get('file_path', '/tmp/cursor_ai_completion.json')
        
        start_time = time.time()
        logger.info(f"Waiting for completion signal (ID: {completion_id}, timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            # Check file-based completion
            if ('file' in methods or 'both' in methods) and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                    
                    # Try to parse as JSON first
                    try:
                        data = json.loads(content)
                        if data.get('completion_id') == completion_id:
                            result.update({
                                'completed': True,
                                'method': 'file_json',
                                'completion_time': time.time() - start_time,
                                'data': data
                            })
                            break
                    except json.JSONDecodeError:
                        # Check for simple completion signal
                        if f'COMPLETED:{completion_id}' in content:
                            result.update({
                                'completed': True,
                                'method': 'file_text',
                                'completion_time': time.time() - start_time,
                                'data': {'raw_content': content}
                            })
                            break
                
                except Exception as e:
                    logger.warning(f"Error reading completion file: {e}")
            
            # TODO: Add HTTP-based completion checking (would require server integration)
            
            time.sleep(1)  # Check every second
        
        if not result['completed']:
            result['timeout'] = True
            result['error'] = f"Completion timeout after {timeout} seconds"
        
        return result
    
    def is_cursor_running(self) -> bool:
        """Check if Cursor is currently running"""
        if self.platform == 'darwin':
            script = '''
            tell application "System Events"
                if exists (processes whose name is "Cursor") then
                    return "true"
                else
                    return "false"
                end if
            end tell
            '''
            success, output, error = self._execute_applescript(script)
            return success and output == "true"
            
        elif self.platform == 'windows':
            script = '''
            Get-Process -Name "Cursor" -ErrorAction SilentlyContinue | Out-Null
            if ($?) { Write-Output "true" } else { Write-Output "false" }
            '''
            success, output, error = self._execute_powershell(script)
            return success and output.strip() == "true"
            
        elif self.platform == 'linux':
            success, output, error = self._execute_xdotool("pgrep -f Cursor")
            return success and output.strip()
        
        return False

# Integration function for SocketIO controller
def create_cursor_ai_injection_handler():
    """Create a handler function that can be used in the SocketIO controller"""
    injector = CursorAIInjector()
    
    def handle_ai_injection(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle AI injection requests from SocketIO
        
        Expected data format:
        {
            "prompt": "Your prompt here",
            "mode": "chat|composer|inline_edit",  # optional, defaults to "chat"
            "delay": 0.5  # optional, defaults to 0.5
        }
        """
        prompt = data.get('prompt', '')
        mode = data.get('mode', 'chat')
        delay = data.get('delay', 0.5)
        
        if not prompt:
            return {
                'success': False,
                'error': 'No prompt provided'
            }
        
        if not injector.is_cursor_running():
            return {
                'success': False,
                'error': 'Cursor is not running'
            }
        
        return injector.inject_prompt(prompt, mode, delay)
    
    return handle_ai_injection

if __name__ == "__main__":
    import sys
    import json
    
    injector = CursorAIInjector()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Test basic functionality
            if injector.is_cursor_running():
                print("✅ Cursor is running")
                result = injector.inject_prompt("Test prompt from automation", "chat")
                print(f"Result: {result}")
            else:
                print("❌ Cursor is not running")
        elif sys.argv[1] == "--json" and len(sys.argv) > 2:
            # JSON mode with full configuration
            try:
                config = json.loads(sys.argv[2])
                prompt = config.get('prompt', '')
                mode = config.get('mode', 'chat')
                delay = config.get('delay', 0.5)
                assume_focused = config.get('assume_focused', False)
                skip_toggle = config.get('skip_toggle', False)
                completion_detection = config.get('completion_detection', None)
                
                if not prompt:
                    print('{"success": false, "error": "No prompt provided in JSON config"}')
                    sys.exit(1)
                
                result = injector.inject_prompt(
                    prompt=prompt,
                    mode=mode,
                    delay=delay,
                    assume_focused=assume_focused,
                    skip_toggle=skip_toggle,
                    completion_detection=completion_detection
                )
                print(f"Injection result: {result}")
                
            except json.JSONDecodeError as e:
                print(f'{{"success": false, "error": "Invalid JSON config: {str(e)}"}}')
                sys.exit(1)
            except Exception as e:
                print(f'{{"success": false, "error": "Error processing JSON config: {str(e)}"}}')
                sys.exit(1)
        else:
            # Simple mode - inject the provided prompt
            prompt = " ".join(sys.argv[1:])
            result = injector.inject_prompt(prompt)
            print(f"Injection result: {result}")
    else:
        print("Usage:")
        print("  python cursor_ai_injector.py '<prompt>'")
        print("  python cursor_ai_injector.py --json '{\"prompt\": \"...\", \"assume_focused\": true}'")
        print("  python cursor_ai_injector.py --test") 