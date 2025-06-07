#!/usr/bin/env python3
"""
Native Messaging Host for Cursor IDE Control
Communicates with the Plasmo Chrome extension to control Cursor IDE
"""

import json
import sys
import struct
import subprocess
import os
import signal
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cursor_controller.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class CursorController:
    def __init__(self):
        self.cursor_executable = self._find_cursor_executable()
        logger.info(f"Cursor executable found at: {self.cursor_executable}")
    
    def _find_cursor_executable(self) -> Optional[str]:
        """Find Cursor IDE executable path"""
        possible_paths = [
            # macOS
            "/Applications/Cursor.app/Contents/MacOS/Cursor",
            "/usr/local/bin/cursor",
            # Linux
            "/usr/bin/cursor",
            "/opt/cursor/cursor",
            "~/.local/bin/cursor",
            # Windows (if running under WSL)
            "/mnt/c/Users/*/AppData/Local/Programs/Cursor/Cursor.exe"
        ]
        
        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path) and os.access(expanded_path, os.X_OK):
                return expanded_path
        
        # Try which/where command
        try:
            result = subprocess.run(['which', 'cursor'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except FileNotFoundError:
            pass
        
        logger.warning("Cursor executable not found")
        return None
    
    def reconnect_mcp_server(self) -> Dict[str, Any]:
        """Reconnect MCP server by restarting Cursor or reloading configuration"""
        try:
            if not self.cursor_executable:
                return {"success": False, "error": "Cursor executable not found"}
            
            # Method 1: Try to reload Cursor configuration using CLI
            # This is a simplified approach - actual implementation may vary
            
            # First, try to find and restart the MCP server process
            try:
                # Look for MCP server processes
                result = subprocess.run(
                    ['pgrep', '-f', 'mcp_server'],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            logger.info(f"Terminating MCP server process {pid}")
                            os.kill(int(pid), signal.SIGTERM)
                
                # Wait a moment and restart
                subprocess.run(['sleep', '2'])
                
                # Try to restart MCP server (adjust path as needed)
                mcp_script_path = "/Users/MikeWolf/Projects/Plasmo/start_mcp.sh"
                if os.path.exists(mcp_script_path):
                    subprocess.Popen([mcp_script_path], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    logger.info("MCP server restart initiated")
                
                return {"success": True, "action": "mcp_reconnect_complete"}
                
            except Exception as e:
                logger.error(f"Error during MCP reconnection: {e}")
                return {"success": False, "error": str(e)}
                
        except Exception as e:
            logger.error(f"Failed to reconnect MCP server: {e}")
            return {"success": False, "error": str(e)}
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open file in Cursor IDE"""
        try:
            if not self.cursor_executable:
                return {"success": False, "error": "Cursor executable not found"}
            
            # Expand user path and resolve
            expanded_path = os.path.expanduser(file_path)
            resolved_path = os.path.abspath(expanded_path)
            
            if not os.path.exists(resolved_path):
                return {"success": False, "error": f"File not found: {resolved_path}"}
            
            # Open file in Cursor
            result = subprocess.run(
                [self.cursor_executable, resolved_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Opened file in Cursor: {resolved_path}")
                return {"success": True, "file_path": resolved_path}
            else:
                logger.error(f"Failed to open file: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": True, "message": "File open command sent (timeout expected)"}
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return {"success": False, "error": str(e)}
    
    def run_command(self, command: str) -> Dict[str, Any]:
        """Execute a command in the context of Cursor"""
        try:
            # Security: Only allow safe commands
            allowed_commands = [
                "cursor --version",
                "cursor --help",
                "cursor --list-extensions",
                "cursor --install-extension",
                "cursor --reload-window"
            ]
            
            if not any(command.startswith(cmd) for cmd in allowed_commands):
                return {"success": False, "error": f"Command not allowed: {command}"}
            
            if not self.cursor_executable:
                return {"success": False, "error": "Cursor executable not found"}
            
            # Execute the command
            cmd_parts = command.split()
            if cmd_parts[0] == "cursor":
                cmd_parts[0] = self.cursor_executable
            
            result = subprocess.run(
                cmd_parts,
                capture_output=True, text=True, timeout=30
            )
            
            logger.info(f"Executed command: {command}")
            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"success": False, "error": str(e)}

class NativeMessagingHost:
    def __init__(self):
        self.controller = CursorController()
        logger.info("Native messaging host initialized")
    
    def read_message(self) -> Optional[Dict[str, Any]]:
        """Read message from stdin"""
        try:
            # Read message length (4 bytes)
            length_bytes = sys.stdin.buffer.read(4)
            if len(length_bytes) != 4:
                return None
            
            message_length = struct.unpack('=I', length_bytes)[0]
            
            # Read message content
            message_bytes = sys.stdin.buffer.read(message_length)
            if len(message_bytes) != message_length:
                return None
            
            message = json.loads(message_bytes.decode('utf-8'))
            logger.debug(f"Received message: {message}")
            return message
            
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None
    
    def send_message(self, message: Dict[str, Any]) -> None:
        """Send message to stdout"""
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            
            # Send message length
            length = len(message_bytes)
            sys.stdout.buffer.write(struct.pack('=I', length))
            
            # Send message content
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()
            
            logger.debug(f"Sent message: {message}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming message and return response"""
        action = message.get('action')
        
        try:
            if action == "reconnect_mcp_server":
                return self.controller.reconnect_mcp_server()
            
            elif action == "open_file":
                file_path = message.get('filePath')
                if not file_path:
                    return {"success": False, "error": "Missing filePath parameter"}
                return self.controller.open_file(file_path)
            
            elif action == "run_command":
                command = message.get('command')
                if not command:
                    return {"success": False, "error": "Missing command parameter"}
                return self.controller.run_command(command)
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {"success": False, "error": str(e)}
    
    def run(self):
        """Main message loop"""
        logger.info("Starting native messaging host")
        
        try:
            while True:
                message = self.read_message()
                if message is None:
                    break
                
                response = self.handle_message(message)
                self.send_message(response)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            logger.info("Native messaging host stopped")

if __name__ == "__main__":
    host = NativeMessagingHost()
    host.run() 