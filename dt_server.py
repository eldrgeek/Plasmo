#!/usr/bin/env python3
"""
Desktop Tools MCP Server
=========================

An MCP (Model Context Protocol) server that provides desktop automation tools
including mouse control, keyboard input, screen capture capabilities, and real-time
input monitoring for enhanced AI conversation context.

Features:
- Mouse operations (click, drag, move)
- Keyboard input (key presses, combinations, text typing)
- Screen capture and screenshot tools
- Window management utilities
- Real-time input monitoring and recording
- Cross-platform desktop automation

Usage:
    python dt_server.py --stdio    # For Cursor IDE
    python dt_server.py            # HTTP mode (development)
    python dt_server.py --help     # Show all options
"""

import asyncio
import json
import time
import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable
from pathlib import Path

# MCP Framework
from fastmcp import FastMCP

# Desktop automation imports
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Enable failsafe (move mouse to corner to stop)
    pyautogui.PAUSE = 0.1      # Default pause between actions
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# Input monitoring imports
try:
    from pynput import keyboard, mouse
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Initialize FastMCP server
mcp = FastMCP("Desktop Tools MCP Server")

# Global configuration
SERVER_VERSION = "1.1.0"  # Updated with input monitoring capabilities
SERVER_BUILD_TIME = datetime.now().isoformat()

# Global state
server_stats = {
    "start_time": time.time(),
    "requests_handled": 0,
    "last_activity": time.time(),
    "mouse_actions": 0,
    "keyboard_actions": 0,
    "screenshots_taken": 0,
    "monitoring_sessions": 0,
    "actions_recorded": 0
}

# Screen dimensions cache
screen_size = None

# Global listener instance
input_listener = None

# ================================
# INPUT MONITORING CLASS
# ================================

class InputListener:
    """Real-time input monitoring class based on YeshieHead listeners.py"""
    
    def __init__(self):
        self.controller = MouseController() if PYNPUT_AVAILABLE else None
        self.recorded_actions = []
        self.pressed_keys = set()
        self.keyboard_listener = None
        self.mouse_listener = None
        self.is_recording = False
        self.string_buffer = ""
        self.callback = None
        self.modifier_keys = {Key.ctrl, Key.cmd, Key.alt, Key.shift} if PYNPUT_AVAILABLE else set()
        self.click_start_time = 0
        self.click_start_pos = (0, 0)
   
    def set_callback(self, callback: Optional[Callable[[str], None]]):
        """Set callback function to receive real-time action events"""
        self.callback = callback
   
    def start_recording(self) -> bool:
        """Start recording user input"""
        if not PYNPUT_AVAILABLE:
            return False
            
        if self.is_recording:
            return True
            
        try:
            self.is_recording = True
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press, 
                on_release=self.on_key_release
            )
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.keyboard_listener.start()
            self.mouse_listener.start()
            
            server_stats["monitoring_sessions"] += 1
            return True
        except Exception:
            self.is_recording = False
            return False

    def stop_recording(self) -> bool:
        """Stop recording user input"""
        if not self.is_recording:
            return True
            
        try:
            self.is_recording = False
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            self.flush_string_buffer()
            return True
        except Exception:
            return False

    def flush_string_buffer(self):
        """Flush accumulated string buffer as a type action"""
        if self.string_buffer:
            self.record_action(f"type: {self.string_buffer}")
            self.string_buffer = ""

    def get_modifier_prefix(self) -> str:
        """Get modifier key prefix string"""
        mods = []
        if Key.ctrl in self.pressed_keys:
            mods.append("ctrl")
        if Key.cmd in self.pressed_keys:
            mods.append("cmd")
        if Key.alt in self.pressed_keys:
            mods.append("alt")
        if Key.shift in self.pressed_keys:
            mods.append("shift")
        return "-".join(mods) + "-" if mods else ""

    def on_key_press(self, key):
        """Handle key press events"""
        if not self.is_recording or not PYNPUT_AVAILABLE:
            return

        if key in self.modifier_keys:
            self.pressed_keys.add(key)
            return

        if isinstance(key, keyboard.KeyCode) or key == Key.space or key == Key.enter:
            if key == Key.space:
                char = " "
            elif key == Key.enter:
                char = "↵"
                if len(self.pressed_keys) > 0:
                    self.flush_string_buffer()
                    modifier_prefix = self.get_modifier_prefix()
                    self.record_action(f"press: {modifier_prefix}{char}")
                    return
            else:
                char = key.char if hasattr(key, 'char') else str(key)
                
            if char:
                has_non_shift_modifiers = (len(self.pressed_keys) > 1) or \
                                        ((len(self.pressed_keys) == 1) and not (Key.shift in self.pressed_keys))
                
                if has_non_shift_modifiers: 
                    self.flush_string_buffer()
                    modifier_prefix = self.get_modifier_prefix()
                    if Key.shift in self.pressed_keys:
                        char = char.upper()
                    self.record_action(f"press: {modifier_prefix}{char}")
                else:
                    if Key.shift in self.pressed_keys:
                        char = char.upper()
                    self.string_buffer += char
        else:
            modifier_prefix = self.get_modifier_prefix()
            key_name = str(key).split('.')[-1]
            self.flush_string_buffer()
            self.record_action(f"press: {modifier_prefix}{key_name}")

    def on_key_release(self, key):
        """Handle key release events"""
        if not self.is_recording:
            return
            
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.is_recording:
            return

        self.flush_string_buffer()
        button_name = self.get_modifier_prefix() + button.name
        
        if pressed:
            self.click_start_time = time.time()
            self.click_start_pos = (x, y)
        else:
            click_duration = time.time() - self.click_start_time
            if click_duration > 1:  # Long press = drag
                self.record_action(f"drag: {button_name} from {self.click_start_pos} to ({x}, {y}) {click_duration:.1f}")
            else:
                self.record_action(f"click: {button_name} {self.click_start_pos}")

    def record_action(self, action: str):
        """Record an action and trigger callback if set"""
        timestamp = datetime.now().isoformat()
        action_entry = {
            "timestamp": timestamp,
            "action": action,
            "session_id": server_stats["monitoring_sessions"]
        }
        
        self.recorded_actions.append(action_entry)
        server_stats["actions_recorded"] += 1
        
        try:
            if self.callback:
                self.callback(action)
        except Exception:
            pass  # Don't let callback errors stop recording

    def get_recorded_actions(self) -> List[Dict[str, Any]]:
        """Get all recorded actions"""
        return make_json_safe(self.recorded_actions)
    
    def clear_recorded_actions(self) -> int:
        """Clear recorded actions and return count of cleared actions"""
        count = len(self.recorded_actions)
        self.recorded_actions.clear()
        self.string_buffer = ""
        return count
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "is_recording": self.is_recording,
            "pynput_available": PYNPUT_AVAILABLE,
            "actions_count": len(self.recorded_actions),
            "string_buffer_length": len(self.string_buffer),
            "pressed_keys_count": len(self.pressed_keys),
            "has_callback": self.callback is not None,
            "session_id": server_stats["monitoring_sessions"]
        }

# ================================
# UTILITY FUNCTIONS
# ================================

def make_json_safe(obj):
    """Convert objects to JSON-serializable format"""
    if hasattr(obj, '__dict__'):
        return {k: make_json_safe(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)

def update_activity():
    """Update server activity timestamp"""
    server_stats["last_activity"] = time.time()
    server_stats["requests_handled"] += 1

def get_screen_size():
    """Get screen dimensions, cached for performance"""
    global screen_size
    if screen_size is None and PYAUTOGUI_AVAILABLE:
        screen_size = pyautogui.size()
    return screen_size

def get_input_listener():
    """Get or create global input listener instance"""
    global input_listener
    if input_listener is None:
        input_listener = InputListener()
    return input_listener

def translate_key(key: str) -> str:
    """
    Translate key names from various formats to pyautogui format.
    Based on YeshieHead controller.py translate_key function.
    """
    pynput_to_pyautogui = {
        'alt_l': 'altleft',
        'alt_r': 'altright',
        'alt_gr': 'altright',
        'caps_lock': 'capslock',
        'cmd': 'command',
        'cmd_l': 'winleft',
        'cmd_r': 'winright',
        'ctrl_l': 'ctrlleft',
        'ctrl_r': 'ctrlright',
        'delete': 'del',
        'esc': 'escape',
        'menu': 'apps',
        'num_lock': 'numlock',
        'page_down': 'pagedown',
        'page_up': 'pageup',
        'print_screen': 'printscreen',
        'scroll_lock': 'scrolllock',
        'shift_l': 'shiftleft',
        'shift_r': 'shiftright',
        'backspace': 'backspace'
    }
    return pynput_to_pyautogui.get(key.lower(), key.lower())

# ================================
# SERVER MANAGEMENT TOOLS
# ================================

@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """
    Get comprehensive server information and status.
    
    Returns:
        Server details including version, uptime, and statistics
    """
    update_activity()
    
    uptime = time.time() - server_stats["start_time"]
    uptime_hours = uptime / 3600
    
    # Get monitoring status
    listener = get_input_listener()
    monitoring_status = listener.get_status()
    
    return {
        "server_name": "Desktop Tools MCP Server",
        "version": SERVER_VERSION,
        "build_time": SERVER_BUILD_TIME,
        "status": "running",
        "uptime_seconds": round(uptime, 2),
        "uptime_hours": round(uptime_hours, 2),
        "requests_handled": server_stats["requests_handled"],
        "last_activity": datetime.fromtimestamp(server_stats["last_activity"]).isoformat(),
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "available_tools": len(mcp.list_tools()),
        "pyautogui_available": PYAUTOGUI_AVAILABLE,
        "pynput_available": PYNPUT_AVAILABLE,
        "screen_size": list(get_screen_size()) if get_screen_size() else None,
        "input_monitoring": monitoring_status,
        "activity_stats": {
            "mouse_actions": server_stats["mouse_actions"],
            "keyboard_actions": server_stats["keyboard_actions"],
            "screenshots_taken": server_stats["screenshots_taken"],
            "monitoring_sessions": server_stats["monitoring_sessions"],
            "actions_recorded": server_stats["actions_recorded"]
        }
    }

@mcp.tool()
def health_check() -> Dict[str, Any]:
    """
    Perform a health check of the server and desktop automation capabilities.
    
    Returns:
        Health status and system information
    """
    update_activity()
    
    try:
        current_time = time.time()
        memory_usage = None
        
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            pass
        
        # Test basic desktop automation
        automation_status = "available" if PYAUTOGUI_AVAILABLE else "unavailable"
        automation_error = None
        
        if PYAUTOGUI_AVAILABLE:
            try:
                # Test basic pyautogui functionality
                current_pos = pyautogui.position()
                screen_size = pyautogui.size()
            except Exception as e:
                automation_status = "error"  
                automation_error = str(e)
        
        # Test input monitoring capabilities
        monitoring_status = "available" if PYNPUT_AVAILABLE else "unavailable"
        monitoring_error = None
        
        if PYNPUT_AVAILABLE:
            try:
                # Test basic pynput functionality
                listener = get_input_listener()
                monitoring_info = listener.get_status()
            except Exception as e:
                monitoring_status = "error"
                monitoring_error = str(e)
        
        return {
            "status": "healthy" if (PYAUTOGUI_AVAILABLE and PYNPUT_AVAILABLE) else "limited",
            "timestamp": datetime.fromtimestamp(current_time).isoformat(),
            "uptime_seconds": current_time - server_stats["start_time"],
            "memory_usage_mb": memory_usage,
            "requests_handled": server_stats["requests_handled"],
            "desktop_automation": {
                "status": automation_status,
                "error": automation_error,
                "pyautogui_version": pyautogui.__version__ if PYAUTOGUI_AVAILABLE else None
            },
            "input_monitoring": {
                "status": monitoring_status,
                "error": monitoring_error,
                "pynput_available": PYNPUT_AVAILABLE
            },
            "last_error": None
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ================================
# MOUSE CONTROL TOOLS
# ================================

@mcp.tool()
def click_mouse(x: int, y: int, button: str = "left", clicks: int = 1, interval: float = 0.0) -> Dict[str, Any]:
    """
    Click the mouse at specified coordinates.
    
    Args:
        x: X coordinate to click
        y: Y coordinate to click  
        button: Mouse button ('left', 'right', 'middle')
        clicks: Number of clicks to perform
        interval: Interval between clicks in seconds
        
    Returns:
        Click operation result
    """
    update_activity()
    server_stats["mouse_actions"] += 1
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        # Validate coordinates
        screen = get_screen_size()
        if screen and (x < 0 or y < 0 or x >= screen.width or y >= screen.height):
            return {"success": False, "error": f"Coordinates ({x}, {y}) outside screen bounds {screen}"}
        
        # Validate button
        valid_buttons = ['left', 'right', 'middle']
        if button not in valid_buttons:
            return {"success": False, "error": f"Invalid button '{button}'. Must be one of: {valid_buttons}"}
        
        # Perform click
        pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
        
        return {
            "success": True,
            "action": "click",
            "coordinates": [x, y],
            "button": button,
            "clicks": clicks,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int, 
               duration: float = 1.0, button: str = "left") -> Dict[str, Any]:
    """
    Drag the mouse from start coordinates to end coordinates.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Duration of drag in seconds
        button: Mouse button to hold during drag
        
    Returns:
        Drag operation result
    """
    update_activity()
    server_stats["mouse_actions"] += 1
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        # Validate coordinates
        screen = get_screen_size()
        if screen:
            for x, y in [(start_x, start_y), (end_x, end_y)]:
                if x < 0 or y < 0 or x >= screen.width or y >= screen.height:
                    return {"success": False, "error": f"Coordinates ({x}, {y}) outside screen bounds {screen}"}
        
        # Move to start position
        pyautogui.moveTo(start_x, start_y)
        time.sleep(0.1)  # Short pause as in YeshieHead controller
        
        # Perform drag
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
        
        return {
            "success": True,
            "action": "drag",
            "start_coordinates": [start_x, start_y],
            "end_coordinates": [end_x, end_y],
            "duration": duration,
            "button": button,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def move_mouse(x: int, y: int, duration: float = 0.0) -> Dict[str, Any]:
    """
    Move the mouse to specified coordinates.
    
    Args:
        x: X coordinate to move to
        y: Y coordinate to move to
        duration: Duration of movement in seconds (0 for instant)
        
    Returns:
        Move operation result
    """
    update_activity()
    server_stats["mouse_actions"] += 1
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        # Validate coordinates
        screen = get_screen_size()
        if screen and (x < 0 or y < 0 or x >= screen.width or y >= screen.height):
            return {"success": False, "error": f"Coordinates ({x}, {y}) outside screen bounds {screen}"}
        
        # Move mouse
        if duration > 0:
            pyautogui.moveTo(x, y, duration=duration)
        else:
            pyautogui.moveTo(x, y)
        
        return {
            "success": True,
            "action": "move",
            "coordinates": [x, y],
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_mouse_position() -> Dict[str, Any]:
    """
    Get the current mouse cursor position.
    
    Returns:
        Current mouse coordinates
    """
    update_activity()
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        pos = pyautogui.position()
        
        return {
            "success": True,
            "position": [pos.x, pos.y],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# KEYBOARD CONTROL TOOLS
# ================================

@mcp.tool()
def press_key(key: str) -> Dict[str, Any]:
    """
    Press a single key or key combination.
    
    Args:
        key: Key to press (e.g., 'a', 'enter', 'ctrl+c', 'cmd+shift+4')
        
    Returns:
        Key press operation result
    """
    update_activity()
    server_stats["keyboard_actions"] += 1
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        if '-' in key:
            # Key combination (e.g., 'ctrl+c', 'cmd+shift+4')
            keys = [translate_key(k.strip()) for k in key.split('-')]
            pyautogui.hotkey(*keys)
            action_type = "hotkey"
        else:
            # Single key
            translated_key = translate_key(key)
            pyautogui.press(translated_key)
            action_type = "press"
        
        return {
            "success": True,
            "action": action_type,
            "key": key,
            "translated_key": keys if '-' in key else translate_key(key),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def type_text(text: str, interval: float = 0.1) -> Dict[str, Any]:
    """
    Type text character by character.
    
    Args:
        text: Text to type
        interval: Interval between keystrokes in seconds
        
    Returns:
        Text typing operation result
    """
    update_activity()
    server_stats["keyboard_actions"] += 1
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        pyautogui.write(text, interval=interval)
        
        return {
            "success": True,
            "action": "type",
            "text": text,
            "length": len(text),
            "interval": interval,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def execute_script(script: str) -> Dict[str, Any]:
    """
    Execute a script of automation commands (based on YeshieHead controller format).
    
    Args:
        script: Multi-line script with commands in format:
                press: key
                type: text
                click: button (x, y)
                drag: button from (x1, y1) to (x2, y2) duration
                
    Returns:
        Script execution result
    """
    update_activity()
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        lines = script.strip().split('\n')
        executed_commands = []
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Add delay between actions
            time.sleep(1.0)  # Same as YeshieHead controller
            
            try:
                if ':' not in line:
                    continue
                    
                action_type, value = line.split(':', 1)
                action_type = action_type.strip()
                value = value.strip()
                
                if action_type == "press":
                    if '-' in value:
                        # Key combination
                        keys = [translate_key(k.strip()) for k in value.split('-')]
                        pyautogui.hotkey(*keys)
                    else:
                        # Single key
                        pyautogui.press(translate_key(value))
                    executed_commands.append(f"pressed: {value}")
                    
                elif action_type == "type":
                    pyautogui.write(value, interval=0.1)
                    executed_commands.append(f"typed: {value}")
                    
                elif action_type.startswith("click"):
                    parts = value.split(' ', 1)
                    button_str = parts[0]
                    pos_str = parts[1]
                    # Parse coordinates: (x, y)
                    x, y = eval(pos_str)
                    pyautogui.click(x, y, button=button_str)
                    executed_commands.append(f"clicked: {button_str} at ({x}, {y})")
                    
                elif action_type.startswith("drag"):
                    parts = value.split()
                    button_str = parts[0]
                    from_pos = tuple(map(float, parts[3].strip('()').split(',')))
                    to_pos = tuple(map(float, parts[5].strip('()').split(',')))
                    duration = float(parts[6])
                    
                    start_x, start_y = from_pos
                    end_x, end_y = to_pos
                    
                    pyautogui.moveTo(start_x, start_y)
                    time.sleep(0.1)
                    pyautogui.dragTo(end_x, end_y, duration=duration, button=button_str)
                    executed_commands.append(f"dragged: {button_str} from ({start_x}, {start_y}) to ({end_x}, {end_y})")
                
                # Small delay between actions  
                time.sleep(0.1)
                
            except Exception as cmd_error:
                errors.append(f"Line {line_num}: {str(cmd_error)}")
                continue
        
        server_stats["keyboard_actions"] += len(executed_commands)
        
        return {
            "success": len(errors) == 0,
            "executed_commands": executed_commands,
            "errors": errors,
            "total_lines": len(lines),
            "executed_count": len(executed_commands),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# SCREEN CAPTURE TOOLS
# ================================

@mcp.tool()
def take_screenshot(filename: str = None, region: List[int] = None) -> Dict[str, Any]:
    """
    Take a screenshot of the screen or a specific region.
    
    Args:
        filename: Optional filename to save screenshot (auto-generated if not provided)
        region: Optional region [x, y, width, height] to capture
        
    Returns:
        Screenshot capture result
    """
    update_activity()
    server_stats["screenshots_taken"] += 1
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Take screenshot
        if region:
            # Capture specific region
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            # Capture full screen
            screenshot = pyautogui.screenshot()
        
        # Save screenshot
        screenshot.save(filename)
        
        return {
            "success": True,
            "filename": filename,
            "region": region,
            "size": screenshot.size,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_screen_info() -> Dict[str, Any]:
    """
    Get information about the screen/display.
    
    Returns:
        Screen information including size and properties
    """
    update_activity()
    
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "error": "PyAutoGUI not available"}
    
    try:
        screen = pyautogui.size()
        
        return {
            "success": True,
            "screen_size": {
                "width": screen.width,
                "height": screen.height
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# INPUT MONITORING TOOLS
# ================================

@mcp.tool()
def start_input_monitoring() -> Dict[str, Any]:
    """
    Start monitoring user input (keyboard and mouse events).
    
    Returns:
        Status of monitoring startup
    """
    update_activity()
    
    if not PYNPUT_AVAILABLE:
        return {
            "success": False, 
            "error": "pynput not available. Install with: pip install pynput"
        }
    
    try:
        listener = get_input_listener()
        success = listener.start_recording()
        
        if success:
            return {
                "success": True,
                "message": "Input monitoring started",
                "status": listener.get_status(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Failed to start input monitoring"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def stop_input_monitoring() -> Dict[str, Any]:
    """
    Stop monitoring user input.
    
    Returns:
        Status of monitoring shutdown
    """
    update_activity()
    
    try:
        listener = get_input_listener()
        success = listener.stop_recording()
        
        if success:
            return {
                "success": True,
                "message": "Input monitoring stopped",
                "status": listener.get_status(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Failed to stop input monitoring"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_recorded_actions(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Get recorded user actions from input monitoring.
    
    Args:
        limit: Maximum number of recent actions to return (None for all)
        
    Returns:
        List of recorded actions with timestamps
    """
    update_activity()
    
    try:
        listener = get_input_listener()
        actions = listener.get_recorded_actions()
        
        if limit is not None and limit > 0:
            actions = actions[-limit:]
        
        return {
            "success": True,
            "actions": actions,
            "total_count": len(listener.recorded_actions),
            "returned_count": len(actions),
            "status": listener.get_status(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def clear_recorded_actions() -> Dict[str, Any]:
    """
    Clear all recorded user actions.
    
    Returns:
        Number of actions that were cleared
    """
    update_activity()
    
    try:
        listener = get_input_listener()
        cleared_count = listener.clear_recorded_actions()
        
        return {
            "success": True,
            "message": f"Cleared {cleared_count} recorded actions",
            "cleared_count": cleared_count,
            "status": listener.get_status(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_monitoring_status() -> Dict[str, Any]:
    """
    Get current input monitoring status and statistics.
    
    Returns:
        Detailed monitoring status information
    """
    update_activity()
    
    try:
        listener = get_input_listener()
        status = listener.get_status()
        
        return {
            "success": True,
            "monitoring_status": status,
            "pynput_available": PYNPUT_AVAILABLE,
            "server_stats": {
                "monitoring_sessions": server_stats["monitoring_sessions"],
                "actions_recorded": server_stats["actions_recorded"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# FILE SYSTEM TOOLS (from template)
# ================================

@mcp.tool()
def read_file(filepath: str) -> Dict[str, Any]:
    """
    Read contents of a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        File contents and metadata
    """
    update_activity()
    
    try:
        file_path = Path(filepath)
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {filepath}"}
        
        if not file_path.is_file():
            return {"success": False, "error": f"Path is not a file: {filepath}"}
        
        # Get file stats
        stat_info = file_path.stat()
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "filepath": str(file_path),
            "content": content,
            "size_bytes": stat_info.st_size,
            "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "lines": len(content.split('\n'))
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def write_file(filepath: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        Write operation result
    """
    update_activity()
    
    try:
        file_path = Path(filepath)
        
        # Create parent directories if requested
        if create_dirs and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        
        # Write file content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Get file stats after writing
        stat_info = file_path.stat()
        
        return {
            "success": True,
            "filepath": str(file_path),
            "size_bytes": stat_info.st_size,
            "lines_written": len(content.split('\n')),
            "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def setup_logging(debug_mode: bool, stdio_mode: bool):
    """Setup appropriate logging based on mode"""
    if debug_mode:
        # Debug mode: log to file with detailed info
        logging.basicConfig(
            level=logging.DEBUG,
            filename='/tmp/dt_server_debug.log',
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    elif stdio_mode:
        # STDIO mode: minimal/no console logging to avoid JSON-RPC interference
        logging.basicConfig(
            level=logging.CRITICAL,
            stream=sys.stderr,
            format='%(message)s'
        )
    else:
        # HTTP mode: normal logging
        logging.basicConfig(
            level=logging.INFO,
            stream=sys.stderr,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(
        description="Desktop Tools MCP Server - Mouse, keyboard, screen automation, and input monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --stdio                    # STDIO mode (for Cursor IDE)
  %(prog)s --http --port 8010         # HTTP mode on port 8010
  %(prog)s --stdio --debug            # STDIO with debug logging
        """
    )
    
    # Transport mode arguments
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        "--stdio", 
        action="store_true", 
        help="Use STDIO transport (default, suitable for Cursor IDE)"
    )
    transport_group.add_argument(
        "--http", 
        action="store_true", 
        help="Use HTTP transport instead of STDIO"
    )
    
    # HTTP mode options
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host to bind to in HTTP mode (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8010,  # Different default port to avoid conflicts
        help="Port to bind to in HTTP mode (default: 8010)"
    )
    
    # Debug options
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging to /tmp/dt_server_debug.log"
    )
    
    args = parser.parse_args()
    
    # Check dependencies availability
    if not PYAUTOGUI_AVAILABLE:
        print("Warning: PyAutoGUI not available. Desktop automation tools will be limited.", file=sys.stderr)
        print("Install with: pip install pyautogui", file=sys.stderr)
    
    if not PYNPUT_AVAILABLE:
        print("Warning: pynput not available. Input monitoring tools will be disabled.", file=sys.stderr)
        print("Install with: pip install pynput", file=sys.stderr)
    
    # Determine transport mode (default to STDIO)
    transport_mode = "stdio"
    if args.http:
        transport_mode = "http"
    
    # Setup logging based on mode
    setup_logging(args.debug, transport_mode == "stdio")
    
    if args.debug:
        logging.info(f"Starting Desktop Tools MCP Server v{SERVER_VERSION}")
        logging.info(f"Transport: {transport_mode}")
        logging.info(f"PyAutoGUI available: {PYAUTOGUI_AVAILABLE}")
        logging.info(f"pynput available: {PYNPUT_AVAILABLE}")
        if transport_mode == "http":
            logging.info(f"HTTP server: {args.host}:{args.port}")
    
    # Run server
    try:
        if transport_mode == "stdio":
            mcp.run()
        else:
            mcp.run(transport="http", host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        if args.debug:
            logging.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 