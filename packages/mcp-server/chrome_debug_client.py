#!/usr/bin/env python3
"""
Chrome Debug Protocol Client
============================

Extracted Chrome debugging functionality from the main MCP server.
Provides clean interface for Chrome DevTools Protocol operations.

Features:
- WebSocket connection management
- Tab discovery and management
- JavaScript execution
- Console log monitoring
- Error handling and recovery
"""

import asyncio
import json
import logging
import time
import threading
import weakref
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests
import websockets
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

class ChromeDebugClient:
    """Chrome Debug Protocol client with connection management."""
    
    def __init__(self, default_host: str = "localhost", default_port: int = 9222):
        self.default_host = default_host
        self.default_port = default_port
        self.instances = {}  # connection_id -> instance info
        self.console_logs = []
        self.console_log_listeners = {}
        self.websocket_connections = {}
        self.connection_lock = threading.Lock()
        self.active_connections = weakref.WeakSet()
    
    def get_connection_id(self, host: str = None, port: int = None) -> str:
        """Get connection identifier string."""
        host = host or self.default_host
        port = port or self.default_port
        return f"{host}:{port}"
    
    @asynccontextmanager
    async def websocket_connection(self, ws_url: str):
        """Context manager for safe WebSocket connections."""
        ws = None
        try:
            ws = await websockets.connect(ws_url)
            self.active_connections.add(ws)
            yield ws
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            raise
        finally:
            if ws:
                self.active_connections.discard(ws)
                await ws.close()
    
    async def send_command_async(self, ws_url: str, command: str, params: Dict = None, timeout: int = 10) -> Dict[str, Any]:
        """
        Send command to Chrome Debug Protocol with proper async handling.
        
        Args:
            ws_url: WebSocket URL for the Chrome tab
            command: Chrome DevTools Protocol command
            params: Command parameters
            timeout: Timeout in seconds
            
        Returns:
            Command response or error
        """
        # CRITICAL: Chrome Debug Protocol requires INTEGER request IDs, not strings
        request_id = int(time.time() * 1000000) % 1000000
        message = {
            "id": request_id,
            "method": command,
            "params": params or {}
        }
        
        try:
            async with self.websocket_connection(ws_url) as websocket:
                # Send command
                await websocket.send(json.dumps(message))
                logger.info(f"Sent Chrome command: {command} with ID: {request_id}")
                
                # Wait for response with timeout
                start_time = time.time()
                messages_received = 0
                while time.time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        messages_received += 1
                        
                        # Skip events, only process our response
                        if data.get("id") == request_id:
                            logger.info(f"Received response for command {command} after {messages_received} messages")
                            return {
                                "success": True,
                                "command": command,
                                "request_id": request_id,
                                "result": data.get("result", {}),
                                "error": data.get("error"),
                                "timestamp": datetime.now().isoformat()
                            }
                        else:
                            # Log events for debugging
                            if "method" in data:
                                logger.info(f"Received event #{messages_received}: {data['method']}")
                            else:
                                logger.info(f"Received unexpected message #{messages_received}: {data}")
                            
                    except asyncio.TimeoutError:
                        logger.info(f"1-second recv timeout, {messages_received} messages so far, continuing...")
                        continue
                
                return {
                    "success": False,
                    "error": f"Timeout waiting for response to {command}",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in Chrome command {command}: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "timestamp": datetime.now().isoformat()
            }
    
    def connect_to_chrome(self, port: int = None, host: str = None) -> Dict[str, Any]:
        """
        Connect to Chrome Debug Protocol with enhanced error handling.
        
        Args:
            port: Chrome debug port
            host: Chrome debug host
            
        Returns:
            Connection information and available tabs
        """
        host = host or self.default_host
        port = port or self.default_port
        connection_id = self.get_connection_id(host, port)
        
        try:
            # Test connection
            response = requests.get(f"http://{host}:{port}/json", timeout=5)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to connect to Chrome debug port {port}",
                    "suggestion": "Ensure Chrome is running with --remote-debugging-port=9222"
                }
            
            tabs_data = response.json()
            
            # Store connection info
            with self.connection_lock:
                self.instances[connection_id] = {
                    "host": host,
                    "port": port,
                    "connected_at": datetime.now().isoformat(),
                    "tabs": len(tabs_data)
                }
            
            logger.info(f"Connected to Chrome at {connection_id} with {len(tabs_data)} tabs")
            
            return {
                "success": True,
                "connection_id": connection_id,
                "host": host,
                "port": port,
                "tabs_available": len(tabs_data),
                "tabs": [
                    {
                        "id": tab.get("id"),
                        "title": tab.get("title", "")[:100],
                        "url": tab.get("url", "")[:200],
                        "type": tab.get("type"),
                        "webSocketDebuggerUrl": tab.get("webSocketDebuggerUrl")
                    }
                    for tab in tabs_data if tab.get("type") in ["page", "background_page"]
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": f"Connection refused to {host}:{port}",
                "suggestion": "Launch Chrome with: ./launch-chrome-debug.sh or chrome --remote-debugging-port=9222"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Timeout connecting to {host}:{port}",
                "suggestion": "Check if Chrome debug port is responsive"
            }
        except Exception as e:
            logger.error(f"Unexpected error connecting to Chrome: {e}")
            return {"success": False, "error": str(e)}
    
    def get_chrome_tabs(self, connection_id: str = None) -> Dict[str, Any]:
        """
        Get available Chrome tabs with enhanced filtering and information.
        
        Args:
            connection_id: Chrome connection identifier
            
        Returns:
            List of available tabs with detailed information
        """
        connection_id = connection_id or self.get_connection_id()
        
        try:
            if connection_id not in self.instances:
                return {
                    "success": False,
                    "error": "Not connected to Chrome. Use connect_to_chrome first.",
                    "available_connections": list(self.instances.keys())
                }
            
            host, port = connection_id.split(":")
            response = requests.get(f"http://{host}:{port}/json", timeout=5)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to get tabs from {connection_id}"}
            
            tabs_data = response.json()
            
            # Filter and enhance tab information
            filtered_tabs = []
            for tab in tabs_data:
                if tab.get("type") in ["page", "background_page"] and tab.get("webSocketDebuggerUrl"):
                    tab_info = {
                        "id": tab.get("id"),
                        "title": self._make_json_safe(tab.get("title", "")[:100]),
                        "url": tab.get("url", "")[:200],
                        "type": tab.get("type"),
                        "webSocketDebuggerUrl": tab.get("webSocketDebuggerUrl"),
                        "favicon": tab.get("faviconUrl", ""),
                        "description": tab.get("description", "")[:100]
                    }
                    
                    # Add extension-specific information
                    if "extension" in tab.get("url", "").lower():
                        tab_info["is_extension"] = True
                        tab_info["extension_type"] = "popup" if "popup" in tab.get("url", "") else "background"
                    
                    filtered_tabs.append(tab_info)
            
            return {
                "success": True,
                "connection_id": connection_id,
                "total_tabs": len(tabs_data),
                "debuggable_tabs": len(filtered_tabs),
                "tabs": filtered_tabs,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting Chrome tabs: {e}")
            return {"success": False, "error": str(e)}
    
    def launch_chrome_debug(self) -> Dict[str, Any]:
        """
        Launch Chrome with debugging enabled and proper configuration.
        
        Returns:
            Launch status and connection information
        """
        try:
            import subprocess
            
            # Use the python launch script
            script_path = Path("./chrome_debug_launcher.py")
            
            if script_path.exists():
                logger.info("Using existing launch script")
                result = subprocess.run(
                    ["python3", str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # Wait a moment for Chrome to start
                    time.sleep(2)
                    
                    # Test connection
                    connection_result = self.connect_to_chrome()
                    
                    return {
                        "success": True,
                        "method": "launch_script",
                        "script_output": result.stdout,
                        "connection_test": connection_result,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.warning(f"Launch script failed: {result.stderr}")
            
            return {
                "success": False,
                "error": "Could not launch Chrome with debugging enabled",
                "suggestions": [
                    "Install Google Chrome",
                    "Run: ./launch-chrome-debug.sh",
                    "Manual: chrome --remote-debugging-port=9222 --remote-allow-origins=*"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error launching Chrome debug: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_javascript(self, code: str, tab_id: str, connection_id: str = None) -> Dict[str, Any]:
        """
        Execute JavaScript in Chrome tab with proper async handling and error reporting.
        
        Args:
            code: JavaScript code to execute
            tab_id: Chrome tab ID
            connection_id: Chrome connection identifier
            
        Returns:
            Execution result with comprehensive error handling
        """
        connection_id = connection_id or self.get_connection_id()
        
        try:
            if connection_id not in self.instances:
                return {"success": False, "error": "Not connected to Chrome. Use connect_to_chrome first."}
            
            # Get WebSocket URL for the tab
            host, port = connection_id.split(":")
            response = requests.get(f"http://{host}:{port}/json", timeout=5)
            
            if response.status_code != 200:
                return {"success": False, "error": "Failed to get tab information"}
            
            tabs = response.json()
            target_tab = None
            
            for tab in tabs:
                if tab.get("id") == tab_id:
                    target_tab = tab
                    break
            
            if not target_tab:
                return {"success": False, "error": f"Tab {tab_id} not found"}
            
            ws_url = target_tab.get("webSocketDebuggerUrl")
            if not ws_url:
                return {"success": False, "error": f"Tab {tab_id} not debuggable"}
            
            # Enable Runtime domain
            enable_result = await self.send_command_async(ws_url, "Runtime.enable")
            if not enable_result.get("success"):
                return {"success": False, "error": "Failed to enable Runtime domain"}
            
            # Execute JavaScript
            exec_result = await self.send_command_async(
                ws_url,
                "Runtime.evaluate",
                {
                    "expression": code,
                    "returnByValue": True,
                    "generatePreview": True
                }
            )
            
            if not exec_result.get("success"):
                return exec_result
            
            result = exec_result.get("result", {})
            
            # Process execution result
            if result.get("exceptionDetails"):
                exception = result["exceptionDetails"]
                return {
                    "success": False,
                    "error": "JavaScript execution error",
                    "exception": self._make_json_safe(exception),
                    "line_number": exception.get("lineNumber"),
                    "column_number": exception.get("columnNumber"),
                    "timestamp": datetime.now().isoformat()
                }
            
            execution_result = result.get("result", {})
            return {
                "success": True,
                "value": self._make_json_safe(execution_result.get("value")),
                "type": execution_result.get("type"),
                "description": execution_result.get("description"),
                "code_executed": code,
                "tab_id": tab_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in JavaScript execution: {e}")
            return {"success": False, "error": str(e)}
    
    def _make_json_safe(self, obj):
        """Convert object to JSON-safe format."""
        if isinstance(obj, (str, int, float, bool, type(None))):
            if isinstance(obj, str):
                try:
                    obj.encode('utf-8', 'strict')
                    return obj
                except UnicodeEncodeError as e:
                    logger.warning(f"Unicode encoding issue: {e}")
                    return obj.encode('utf-8', 'replace').decode('utf-8')
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {str(k): self._make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_safe(item) for item in obj]
        else:
            try:
                str_obj = str(obj)
                str_obj.encode('utf-8', 'strict')
                return str_obj
            except UnicodeEncodeError:
                return str(obj).encode('utf-8', 'replace').decode('utf-8')
    
    async def cleanup_all(self):
        """Clean up all Chrome Debug Protocol resources."""
        logger.info("Cleaning up Chrome Debug Protocol resources...")
        
        # Close all WebSocket connections
        connections_to_close = list(self.active_connections)
        for ws in connections_to_close:
            try:
                if hasattr(ws, 'close'):
                    await ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        # Clear instance data
        with self.connection_lock:
            self.instances.clear()
            self.console_logs.clear()
            self.console_log_listeners.clear()
            self.websocket_connections.clear()
        
        logger.info(f"Cleaned up {len(connections_to_close)} WebSocket connections")


def create_chrome_debug_tools(mcp: FastMCP, client: ChromeDebugClient):
    """Create MCP tools for Chrome Debug Protocol operations."""
    
    @mcp.tool()
    def connect_to_chrome(port: int = 9222, host: str = "localhost") -> Dict[str, Any]:
        """
        Connect to Chrome Debug Protocol with enhanced error handling.
        
        Args:
            port: Chrome debug port
            host: Chrome debug host
            
        Returns:
            Connection information and available tabs
        """
        return client.connect_to_chrome(port, host)
    
    @mcp.tool()
    def get_chrome_tabs(connection_id: str = "localhost:9222") -> Dict[str, Any]:
        """
        Get available Chrome tabs with enhanced filtering and information.
        
        Args:
            connection_id: Chrome connection identifier
            
        Returns:
            List of available tabs with detailed information
        """
        return client.get_chrome_tabs(connection_id)
    
    @mcp.tool()
    def launch_chrome_debug() -> Dict[str, Any]:
        """
        Launch Chrome with debugging enabled and proper configuration.
        
        Returns:
            Launch status and connection information
        """
        return client.launch_chrome_debug()
    
    @mcp.tool()
    def execute_javascript(code: str, tab_id: str, connection_id: str = "localhost:9222") -> Dict[str, Any]:
        """
        Execute JavaScript in Chrome tab with proper async handling and error reporting.
        
        Args:
            code: JavaScript code to execute
            tab_id: Chrome tab ID
            connection_id: Chrome connection identifier
            
        Returns:
            Execution result with comprehensive error handling
        """
        import asyncio
        import concurrent.futures
        
        def run_async_execution():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(client.execute_javascript(code, tab_id, connection_id))
            except Exception as e:
                logger.error(f"Error in JavaScript execution: {e}")
                return {"success": False, "error": str(e)}
            finally:
                loop.close()
        
        try:
            # Run in separate thread to avoid blocking
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_execution)
                result = future.result(timeout=30)  # 30 second timeout
                
            return client._make_json_safe(result)
            
        except concurrent.futures.TimeoutError:
            return {"success": False, "error": "JavaScript execution timed out"}
        except Exception as e:
            logger.error(f"Unexpected error in JavaScript execution: {e}")
            return {"success": False, "error": str(e)} 