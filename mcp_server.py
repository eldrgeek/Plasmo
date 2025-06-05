#!/usr/bin/env python3
"""
FastMCP Server for Cursor Integration
==========================================

This is a Model Context Protocol (MCP) server using fastMCP with multiple transport support.
It provides tools that can be used by AI assistants in Cursor IDE and other MCP clients.

Setup Instructions:
1. Install dependencies: pip install fastmcp uvicorn websockets aiohttp pychrome
2. Run server in HTTP mode: python mcp_server.py
3. Run server in stdio mode: python mcp_server.py --stdio
4. Add to Cursor settings (see bottom of file for config)
5. Restart Cursor

Features:
- File operations (read, write, list)
- Code analysis tools
- Project structure analysis
- Git operations
- Database utilities
- Chrome Debug Protocol integration for console logs and debugging

Transport Modes:
- HTTP (default): For web-based deployments and Cursor integration
- STDIO: For local tools and command-line integration (e.g., Claude Desktop)
"""

import os
import json
import subprocess
import sqlite3
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import asyncio
import time
import threading
from datetime import datetime

# Chrome Debug Protocol imports
import websockets
import aiohttp
import pychrome
import requests

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Cursor Development Assistant")

# Configuration
SERVER_PORT = 8000
SERVER_HOST = "127.0.0.1"

# Chrome Debug Protocol configuration
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_HOST = "localhost"

# Global variables for Chrome connection management
chrome_instances = {}
console_logs = []
console_log_listeners = {}

def make_json_safe(obj):
    """Convert object to JSON-safe format."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    else:
        # Convert any other object to string
        return str(obj)

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success or error message
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_files(directory: str = ".", pattern: str = "*", recursive: bool = False) -> List[str]:
    """
    List files in a directory.
    
    Args:
        directory: Directory path to list files from
        pattern: File pattern to match (e.g., "*.py", "*.js")
        recursive: Whether to search recursively
        
    Returns:
        List of file paths
    """
    try:
        path = Path(directory)
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        return [str(f) for f in files if f.is_file()]
    except Exception as e:
        return [f"Error listing files: {str(e)}"]

@mcp.tool()
def get_project_structure(directory: str = ".", max_depth: int = 3) -> Dict[str, Any]:
    """
    Get the structure of a project directory.
    
    Args:
        directory: Root directory to analyze
        max_depth: Maximum depth to traverse
        
    Returns:
        Dictionary representing the project structure
    """
    def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
        if current_depth >= max_depth:
            return {}
        
        result = {}
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    result[item.name + "/"] = build_tree(item, current_depth + 1)
                else:
                    result[item.name] = {
                        "size": item.stat().st_size,
                        "type": "file"
                    }
        except PermissionError:
            result["<permission_denied>"] = {}
        
        return result
    
    try:
        return build_tree(Path(directory))
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_code(file_path: str) -> Dict[str, Any]:
    """
    Analyze a code file for basic metrics.
    
    Args:
        file_path: Path to the code file
        
    Returns:
        Dictionary with code analysis results
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        analysis = {
            "file_path": file_path,
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": 0,
            "function_count": 0,
            "class_count": 0,
            "import_count": 0
        }
        
        # Basic analysis based on file extension
        ext = Path(file_path).suffix.lower()
        
        for line in lines:
            stripped = line.strip()
            
            if ext == '.py':
                if stripped.startswith('#'):
                    analysis["comment_lines"] += 1
                elif stripped.startswith('def '):
                    analysis["function_count"] += 1
                elif stripped.startswith('class '):
                    analysis["class_count"] += 1
                elif stripped.startswith(('import ', 'from ')):
                    analysis["import_count"] += 1
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                if stripped.startswith('//') or stripped.startswith('/*'):
                    analysis["comment_lines"] += 1
                elif 'function ' in stripped or '=>' in stripped:
                    analysis["function_count"] += 1
                elif 'class ' in stripped:
                    analysis["class_count"] += 1
                elif stripped.startswith(('import ', 'const ', 'require(')):
                    analysis["import_count"] += 1
        
        return analysis
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def run_git_command(command: str, directory: str = ".") -> str:
    """
    Run a git command and return the output.
    
    Args:
        command: Git command to run (without 'git' prefix)
        directory: Directory to run the command in
        
    Returns:
        Command output or error message
    """
    try:
        # Security: only allow safe git commands
        safe_commands = [
            'status', 'log', 'branch', 'diff', 'show',
            'ls-files', 'rev-parse', 'config --list'
        ]
        
        if not any(command.startswith(safe_cmd) for safe_cmd in safe_commands):
            return "Error: Only read-only git commands are allowed"
        
        result = subprocess.run(
            ['git'] + command.split(),
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Git error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error running git command: {str(e)}"

@mcp.tool()
def search_in_files(pattern: str, directory: str = ".", file_pattern: str = "*", case_sensitive: bool = False) -> List[Dict[str, Any]]:
    """
    Search for a pattern in files.
    
    Args:
        pattern: Text pattern to search for
        directory: Directory to search in
        file_pattern: File pattern to match (e.g., "*.py")
        case_sensitive: Whether search should be case sensitive
        
    Returns:
        List of matches with file, line number, and content
    """
    try:
        matches = []
        path = Path(directory)
        
        for file_path in path.rglob(file_pattern):
            if not file_path.is_file():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        search_line = line if case_sensitive else line.lower()
                        search_pattern = pattern if case_sensitive else pattern.lower()
                        
                        if search_pattern in search_line:
                            matches.append({
                                "file": str(file_path),
                                "line_number": line_num,
                                "content": line.strip(),
                                "match": pattern
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return matches
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_sqlite_db(db_path: str, schema_sql: str) -> str:
    """
    Create a SQLite database with given schema.
    
    Args:
        db_path: Path for the database file
        schema_sql: SQL commands to create the schema
        
    Returns:
        Success or error message
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(schema_sql)
        
        conn.commit()
        conn.close()
        
        return f"Successfully created database at {db_path}"
    except Exception as e:
        return f"Error creating database: {str(e)}"

@mcp.tool()
def query_sqlite_db(db_path: str, query: str) -> List[Dict[str, Any]]:
    """
    Query a SQLite database.
    
    Args:
        db_path: Path to the database file
        query: SQL query to execute
        
    Returns:
        Query results as list of dictionaries
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_system_info() -> Dict[str, Any]:
    """
    Get system information useful for development.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": dict(os.environ),
        "path_separator": os.pathsep,
        "file_separator": os.sep
    }

# Add server info endpoint
@mcp.tool()
def server_info() -> Dict[str, str]:
    """Get information about this MCP server."""
    # Get tools by calling the list_tools method
    tools_list = []
    try:
        # Get all tool names from the server
        tools_list = list(mcp.tools.keys()) if hasattr(mcp, 'tools') else []
    except:
        tools_list = []
    
    return {
        "name": "Cursor Development Assistant",
        "version": "1.0.0",
        "description": "MCP server providing development tools for Cursor IDE",
        "transport": "HTTP",
        "tools_count": str(len(tools_list)),
        "available_tools": tools_list
    }

# Chrome Debug Protocol Tools
# ===========================

@mcp.tool()
def connect_to_chrome(port: int = 9222, host: str = "localhost") -> Dict[str, Any]:
    """
    Connect to a Chrome instance running with debug mode enabled.
    
    Args:
        port: Chrome debug port (default: 9222)
        host: Chrome debug host (default: localhost)
        
    Returns:
        Connection status and available tabs
    """
    try:
        # Get tabs directly from Chrome's HTTP API instead of using pychrome objects
        response = requests.get(f"http://{host}:{port}/json", timeout=5)
        tabs_data = response.json()
        
        # Create browser instance for other operations
        browser = pychrome.Browser(url=f"http://{host}:{port}")
        
        # Store browser instance for later use
        connection_id = f"{host}:{port}"
        chrome_instances[connection_id] = browser
        
        # Extract clean tab information from the HTTP API response
        tab_list = []
        for tab_data in tabs_data:
            tab_info = {
                "id": str(tab_data.get("id", "")),
                "title": str(tab_data.get("title", "")),
                "url": str(tab_data.get("url", "")),
                "type": str(tab_data.get("type", "page"))
            }
            tab_list.append(tab_info)
        
        return {
            "status": "connected",
            "connection_id": connection_id,
            "tabs_count": len(tab_list),
            "tabs": tab_list
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "suggestion": "Make sure Chrome is running with --remote-debugging-port=9222"
        }

@mcp.tool()
def get_chrome_tabs(connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Get list of available Chrome tabs for debugging.
    
    Args:
        connection_id: Chrome connection identifier
        
    Returns:
        List of available tabs
    """
    try:
        if connection_id not in chrome_instances:
            return {"error": "Not connected to Chrome. Use connect_to_chrome first."}
        
        # Extract host and port from connection_id
        host, port = connection_id.split(":")
        
        # Get tabs directly from Chrome's HTTP API
        response = requests.get(f"http://{host}:{port}/json", timeout=5)
        tabs_data = response.json()
        
        # Extract clean tab information
        tab_list = []
        for tab_data in tabs_data:
            tab_info = {
                "id": str(tab_data.get("id", "")),
                "title": str(tab_data.get("title", "")),
                "url": str(tab_data.get("url", "")),
                "type": str(tab_data.get("type", "page")),
                "description": str(tab_data.get("description", "")),
                "websocket_debug_url": str(tab_data.get("webSocketDebuggerUrl", ""))
            }
            tab_list.append(tab_info)
        
        return {
            "tabs": tab_list
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def start_console_monitoring(tab_id: str, connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Start monitoring console logs for a specific Chrome tab.
    
    Args:
        tab_id: Chrome tab ID to monitor
        connection_id: Chrome connection identifier
        
    Returns:
        Status of console monitoring setup
    """
    try:
        if connection_id not in chrome_instances:
            return {"error": "Not connected to Chrome. Use connect_to_chrome first."}
        
        # Extract host and port from connection_id
        host, port = connection_id.split(":")
        
        # Verify the tab exists
        response = requests.get(f"http://{host}:{port}/json", timeout=5)
        tabs_data = response.json()
        
        tab_found = False
        tab_info = None
        for tab_data in tabs_data:
            if tab_data.get("id") == tab_id:
                tab_found = True
                tab_info = tab_data
                break
        
        if not tab_found:
            return {"error": f"Tab with ID {tab_id} not found"}
        
        # Get the WebSocket URL for this tab
        ws_url = tab_info.get("webSocketDebuggerUrl")
        if not ws_url:
            return {"error": f"No WebSocket URL available for tab {tab_id}"}
        
        # Clear existing logs for this tab
        listener_key = f"{connection_id}:{tab_id}"
        if listener_key not in console_log_listeners:
            console_log_listeners[listener_key] = []
        
        # Store the WebSocket URL for later use
        console_log_listeners[listener_key].append({
            "timestamp": datetime.now().isoformat(),
            "tab_id": str(tab_id),
            "connection_id": str(connection_id),
            "level": "info",
            "text": f"Started monitoring tab: {tab_info.get('title', 'Unknown')}",
            "source": "mcp-server",
            "websocket_url": ws_url
        })
        
        return {
            "status": "monitoring_started",
            "tab_id": str(tab_id),
            "connection_id": str(connection_id),
            "listener_key": str(listener_key),
            "tab_title": str(tab_info.get("title", "")),
            "tab_url": str(tab_info.get("url", "")),
            "tab_type": str(tab_info.get("type", "")),
            "websocket_url": ws_url,
            "note": "Use execute_javascript() to inject console logs or interact with the tab"
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_console_logs(tab_id: str = None, connection_id: str = "localhost:9222", limit: int = 50) -> Dict[str, Any]:
    """
    Retrieve console logs from Chrome debugging session.
    
    Args:
        tab_id: Specific tab ID to get logs from (optional, gets all if not specified)
        connection_id: Chrome connection identifier
        limit: Maximum number of logs to return
        
    Returns:
        List of console log entries
    """
    try:
        if tab_id:
            listener_key = f"{connection_id}:{tab_id}"
            if listener_key in console_log_listeners:
                logs = console_log_listeners[listener_key][-limit:]
            else:
                logs = [log for log in console_logs if log["tab_id"] == str(tab_id)][-limit:]
        else:
            logs = console_logs[-limit:]
        
        return {
            "logs": logs,
            "total_logs": len(logs),
            "tab_id": str(tab_id) if tab_id else None,
            "connection_id": str(connection_id)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def clear_console_logs(tab_id: str = None, connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Clear console logs for a specific tab or all tabs.
    
    Args:
        tab_id: Specific tab ID to clear logs from (optional, clears all if not specified)
        connection_id: Chrome connection identifier
        
    Returns:
        Status of log clearing operation
    """
    try:
        if tab_id:
            listener_key = f"{connection_id}:{tab_id}"
            if listener_key in console_log_listeners:
                cleared_count = len(console_log_listeners[listener_key])
                console_log_listeners[listener_key] = []
                
                # Also remove from global logs
                global console_logs
                console_logs = [log for log in console_logs if log["tab_id"] != str(tab_id)]
                
                return {
                    "status": "cleared",
                    "tab_id": str(tab_id),
                    "cleared_count": cleared_count
                }
            else:
                return {"status": "no_logs", "tab_id": str(tab_id)}
        else:
            # Clear all logs
            total_cleared = len(console_logs)
            console_logs.clear()
            for key in console_log_listeners:
                console_log_listeners[key] = []
            
            return {
                "status": "all_cleared",
                "cleared_count": total_cleared
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def execute_javascript(code: str, tab_id: str, connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Execute JavaScript code in a Chrome tab for debugging.
    
    Args:
        code: JavaScript code to execute
        tab_id: Chrome tab ID to execute code in
        connection_id: Chrome connection identifier
        
    Returns:
        Execution result
    """
    try:
        if connection_id not in chrome_instances:
            return {"error": "Not connected to Chrome. Use connect_to_chrome first."}
        
        # Extract host and port from connection_id
        host, port = connection_id.split(":")
        
        # Get tab information
        response = requests.get(f"http://{host}:{port}/json", timeout=5)
        tabs_data = response.json()
        
        tab_info = None
        for tab_data in tabs_data:
            if tab_data.get("id") == tab_id:
                tab_info = tab_data
                break
        
        if not tab_info:
            return {"error": f"Tab with ID {tab_id} not found"}
        
        # Get the WebSocket URL
        ws_url = tab_info.get("webSocketDebuggerUrl")
        if not ws_url:
            return {"error": f"No WebSocket URL available for tab {tab_id}"}
        
        # Use WebSocket to execute JavaScript
        import websocket
        
        ws = websocket.create_connection(ws_url, timeout=10)
        
        # Enable Runtime domain
        ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
        enable_result = ws.recv()
        
        # Execute the JavaScript code
        ws.send(json.dumps({
            'id': 2, 
            'method': 'Runtime.evaluate', 
            'params': {
                'expression': code,
                'returnByValue': True
            }
        }))
        
        execution_result = ws.recv()
        ws.close()
        
        # Parse the result
        result_data = json.loads(execution_result)
        
        if result_data.get("id") == 2 and "result" in result_data:
            execution_data = result_data["result"]
            
            # Clean the result to be JSON-safe
            clean_result = {}
            if execution_data and "result" in execution_data:
                result_obj = execution_data["result"]
                clean_result = {
                    "type": str(result_obj.get("type", "")),
                    "value": make_json_safe(result_obj.get("value")),
                    "description": str(result_obj.get("description", "")) if result_obj.get("description") else None
                }
            
            # Check for exceptions
            exception_details = execution_data.get("exceptionDetails")
            if exception_details:
                return {
                    "success": False,
                    "error": str(exception_details.get("text", "JavaScript execution failed")),
                    "exception": make_json_safe(exception_details),
                    "tab_id": str(tab_id),
                    "connection_id": str(connection_id)
                }
            
            return {
                "success": True,
                "result": clean_result,
                "tab_id": str(tab_id),
                "connection_id": str(connection_id),
                "tab_title": str(tab_info.get("title", "")),
                "tab_type": str(tab_info.get("type", ""))
            }
        else:
            return {
                "success": False,
                "error": "Unexpected response format",
                "raw_response": make_json_safe(result_data),
                "tab_id": str(tab_id),
                "connection_id": str(connection_id)
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tab_id": str(tab_id),
            "connection_id": str(connection_id)
        }

@mcp.tool()
def set_breakpoint(url: str, line_number: int, tab_id: str, connection_id: str = "localhost:9222", condition: str = None) -> Dict[str, Any]:
    """
    Set a breakpoint in Chrome DevTools for debugging.
    
    Args:
        url: URL or file path where to set the breakpoint
        line_number: Line number for the breakpoint
        tab_id: Chrome tab ID
        connection_id: Chrome connection identifier
        condition: Optional condition for conditional breakpoint
        
    Returns:
        Breakpoint setting result
    """
    try:
        if connection_id not in chrome_instances:
            return {"error": "Not connected to Chrome. Use connect_to_chrome first."}
        
        browser = chrome_instances[connection_id]
        tab = browser.get_tab(tab_id)
        
        # Enable Debugger domain
        tab.Debugger.enable()
        
        # Set breakpoint
        if condition:
            result = tab.Debugger.setBreakpointByUrl(
                lineNumber=line_number,
                url=url,
                condition=condition
            )
        else:
            result = tab.Debugger.setBreakpointByUrl(
                lineNumber=line_number,
                url=url
            )
        
        # Clean the result
        actual_location = result.get("actualLocation", {})
        clean_location = {}
        if actual_location:
            clean_location = {
                "lineNumber": int(actual_location.get("lineNumber", line_number)),
                "columnNumber": int(actual_location.get("columnNumber", 0)),
                "scriptId": str(actual_location.get("scriptId", ""))
            }
        
        return {
            "success": True,
            "breakpoint_id": str(result.get("breakpointId", "")),
            "actual_location": clean_location,
            "url": str(url),
            "line_number": int(line_number),
            "condition": str(condition) if condition else None,
            "tab_id": str(tab_id),
            "connection_id": str(connection_id)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": str(url),
            "line_number": int(line_number),
            "tab_id": str(tab_id),
            "connection_id": str(connection_id)
        }

@mcp.tool()
def get_chrome_debug_info(connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Get comprehensive debugging information about the Chrome instance.
    
    Args:
        connection_id: Chrome connection identifier
        
    Returns:
        Debugging information including tabs, logs count, and connection status
    """
    try:
        info = {
            "connection_id": str(connection_id),
            "connected": connection_id in chrome_instances,
            "total_console_logs": len(console_logs),
            "active_listeners": len(console_log_listeners),
            "listener_details": {}
        }
        
        if connection_id in chrome_instances:
            try:
                # Extract host and port from connection_id
                host, port = connection_id.split(":")
                
                # Get tabs directly from Chrome's HTTP API
                response = requests.get(f"http://{host}:{port}/json", timeout=5)
                tabs_data = response.json()
                
                info["tabs"] = [
                    {
                        "id": str(tab_data.get("id", "")),
                        "title": str(tab_data.get("title", "")),
                        "url": str(tab_data.get("url", "")),
                        "type": str(tab_data.get("type", "page"))
                    }
                    for tab_data in tabs_data
                ]
            except Exception as tab_error:
                info["tabs"] = []
                info["tab_error"] = str(tab_error)
        else:
            info["tabs"] = []
        
        # Add listener details
        for listener_key, logs in console_log_listeners.items():
            info["listener_details"][str(listener_key)] = {
                "log_count": len(logs),
                "latest_log": logs[-1]["timestamp"] if logs else None
            }
        
        return info
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def launch_chrome_debug() -> Dict[str, Any]:
    """
    Launch Chrome with debugging enabled on the configured port.
    
    Returns:
        Status of Chrome launch attempt
    """
    try:
        # Chrome command with debugging flags
        chrome_cmd = [
            "google-chrome",  # or "chrome" on some systems
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--user-data-dir=./chrome-debug-profile"
        ]
        
        # Try different Chrome executable names
        chrome_names = ["google-chrome", "chrome", "chromium", "chromium-browser", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        
        launched = False
        for chrome_name in chrome_names:
            try:
                chrome_cmd[0] = chrome_name
                subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                launched = True
                break
            except FileNotFoundError:
                continue
        
        if not launched:
            return {
                "status": "failed",
                "error": "Chrome executable not found",
                "suggestion": "Make sure Chrome is installed and accessible in PATH"
            }
        
        # Wait a moment for Chrome to start
        time.sleep(2)
        
        return {
            "status": "launched",
            "debug_port": CHROME_DEBUG_PORT,
            "debug_url": f"http://{CHROME_DEBUG_HOST}:{CHROME_DEBUG_PORT}",
            "next_step": "Use connect_to_chrome() to establish connection"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="FastMCP Server with Chrome Debug Protocol Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport Modes:
  HTTP (default)    Run as HTTP server for web-based deployments and Cursor IDE
  STDIO             Run as STDIO server for local tools and Claude Desktop

Examples:
  python mcp_server.py                    # Run in HTTP mode (default)
  python mcp_server.py --stdio            # Run in STDIO mode
  python mcp_server.py --http             # Explicitly run in HTTP mode
  python mcp_server.py --port 9000        # Run in HTTP mode on port 9000
  python mcp_server.py --host 0.0.0.0     # Run in HTTP mode on all interfaces
        """
    )
    
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        '--stdio', 
        action='store_true',
        help='Run server in STDIO mode for local tools and command-line integration'
    )
    transport_group.add_argument(
        '--http', 
        action='store_true',
        help='Run server in HTTP mode (default)'
    )
    
    # HTTP-specific options
    parser.add_argument(
        '--host',
        default=SERVER_HOST,
        help=f'Host to bind HTTP server to (default: {SERVER_HOST})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=SERVER_PORT,
        help=f'Port to bind HTTP server to (default: {SERVER_PORT})'
    )
    parser.add_argument(
        '--path',
        default='/mcp',
        help='Path for HTTP server endpoint (default: /mcp)'
    )
    
    args = parser.parse_args()
    
    # Determine transport mode
    use_stdio = args.stdio
    
    # Get tools count for display
    tools_count = 0
    tools_list = []
    try:
        tools_list = list(mcp.tools.keys()) if hasattr(mcp, 'tools') else []
        tools_count = len(tools_list)
    except:
        # Fallback - count the decorated functions
        tools_count = 19  # Updated count including Chrome debugging tools
        tools_list = [
            "read_file", "write_file", "list_files", "get_project_structure",
            "analyze_code", "run_git_command", "search_in_files", 
            "create_sqlite_db", "query_sqlite_db", "get_system_info", "server_info",
            # Chrome Debug Protocol tools
            "connect_to_chrome", "get_chrome_tabs", "start_console_monitoring",
            "get_console_logs", "clear_console_logs", "execute_javascript",
            "set_breakpoint", "get_chrome_debug_info", "launch_chrome_debug"
        ]
    
    if use_stdio:
        print(f"""
🚀 FastMCP Server Starting (STDIO Mode)
========================================
Transport: STDIO
Tools available: {tools_count}

🔧 Chrome Debug Protocol Support Added!
Chrome Debug Port: {CHROME_DEBUG_PORT}
Use launch_chrome_debug() to start Chrome with debugging enabled

📝 STDIO Mode Configuration:
This server is running in STDIO mode for local tools and command-line integration.
Perfect for use with Claude Desktop and other MCP clients that manage server processes.

To use with Claude Desktop:
1. Add this to your Claude Desktop configuration:
{{
  "mcpServers": {{
    "cursor-dev-assistant": {{
      "command": "python",
      "args": ["{os.path.abspath(__file__)}", "--stdio"]
    }}
  }}
}}

2. Restart Claude Desktop
3. The tools will be available in conversations

Available Tools:
""", file=sys.stderr)
    else:
        print(f"""
🚀 FastMCP Server Starting (HTTP Mode)
======================================
Server: http://{args.host}:{args.port}{args.path}
Transport: HTTP
Tools available: {tools_count}

🔧 Chrome Debug Protocol Support Added!
Chrome Debug Port: {CHROME_DEBUG_PORT}
Use launch_chrome_debug() to start Chrome with debugging enabled

To integrate with Cursor:
1. Open Cursor settings (Cmd/Ctrl + ,)
2. Search for "mcp" or "Model Context Protocol"
3. Add this configuration:

{{
  "mcpServers": {{
    "cursor-dev-assistant": {{
      "url": "http://{args.host}:{args.port}{args.path}"
    }}
  }}
}}

4. Restart Cursor
5. The tools will be available in AI conversations

Available Tools:
""")
    
    # Group tools by category for better display
    file_tools = ["read_file", "write_file", "list_files", "get_project_structure"]
    code_tools = ["analyze_code", "run_git_command", "search_in_files"]
    db_tools = ["create_sqlite_db", "query_sqlite_db"]
    chrome_tools = ["launch_chrome_debug", "connect_to_chrome", "get_chrome_tabs", 
                   "start_console_monitoring", "get_console_logs", "clear_console_logs",
                   "execute_javascript", "set_breakpoint", "get_chrome_debug_info"]
    system_tools = ["get_system_info", "server_info"]
    
    output_file = sys.stderr if use_stdio else sys.stdout
    
    print("📁 File Operations:", file=output_file)
    for tool in file_tools:
        if tool in tools_list:
            print(f"  • {tool}", file=output_file)
    
    print("\n💻 Code Analysis:", file=output_file)
    for tool in code_tools:
        if tool in tools_list:
            print(f"  • {tool}", file=output_file)
    
    print("\n🗄️ Database Tools:", file=output_file)
    for tool in db_tools:
        if tool in tools_list:
            print(f"  • {tool}", file=output_file)
    
    print("\n🌐 Chrome Debug Protocol:", file=output_file)
    for tool in chrome_tools:
        if tool in tools_list:
            print(f"  • {tool}", file=output_file)
    
    print("\n⚙️ System Tools:", file=output_file)
    for tool in system_tools:
        if tool in tools_list:
            print(f"  • {tool}", file=output_file)
    
    print("\n" + "="*50, file=output_file)
    print("🚀 Chrome Debugging Quick Start:", file=output_file)
    print("1. Use launch_chrome_debug() to start Chrome with debugging", file=output_file)
    print("2. Use connect_to_chrome() to establish connection", file=output_file)
    print("3. Use get_chrome_tabs() to see available tabs", file=output_file)
    print("4. Use start_console_monitoring(tab_id) to monitor console logs", file=output_file)
    print("5. Use get_console_logs() to retrieve captured logs", file=output_file)
    print("="*50, file=output_file)
    
    # Start the server using appropriate transport
    if use_stdio:
        print("🎯 Server ready - listening on STDIO", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        print(f"🎯 Server starting on http://{args.host}:{args.port}{args.path}")
        mcp.run(
            transport="streamable-http",
            host=args.host, 
            port=args.port,
            path=args.path
        )

"""
INTEGRATION INSTRUCTIONS:
========================

HTTP Mode (Default - for Cursor IDE):
====================================

1. Save this file as 'mcp_server.py'

2. Install dependencies:
   pip install fastmcp uvicorn websockets aiohttp pychrome

3. Run the server:
   python mcp_server.py

4. Configure Cursor:
   - Open Cursor settings (Cmd/Ctrl + ,)
   - Search for "mcp" 
   - Add this to your settings.json:

{
  "mcpServers": {
    "cursor-dev-assistant": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}

5. Restart Cursor

STDIO Mode (for Claude Desktop and local tools):
==============================================

1. Run the server in STDIO mode:
   python mcp_server.py --stdio

2. Configure Claude Desktop:
   - Open Claude Desktop settings
   - Add this configuration:

{
  "mcpServers": {
    "cursor-dev-assistant": {
      "command": "python",
      "args": ["/path/to/mcp_server.py", "--stdio"]
    }
  }
}

3. Restart Claude Desktop

Command Line Options:
===================

python mcp_server.py                    # HTTP mode (default)
python mcp_server.py --stdio            # STDIO mode
python mcp_server.py --http             # Explicitly HTTP mode
python mcp_server.py --port 9000        # Custom port
python mcp_server.py --host 0.0.0.0     # Bind to all interfaces
python mcp_server.py --path /custom     # Custom HTTP path

AVAILABLE TOOLS:
- read_file: Read file contents
- write_file: Write to files
- list_files: List directory contents
- get_project_structure: Analyze project layout
- analyze_code: Get code metrics
- run_git_command: Safe git operations
- search_in_files: Text search across files
- create_sqlite_db: Create databases
- query_sqlite_db: Query databases
- get_system_info: System information
- server_info: MCP server details

🌐 CHROME DEBUG PROTOCOL TOOLS:
- launch_chrome_debug: Launch Chrome with debugging enabled
- connect_to_chrome: Connect to Chrome debug instance
- get_chrome_tabs: List available browser tabs
- start_console_monitoring: Begin monitoring console output
- get_console_logs: Retrieve captured console logs
- clear_console_logs: Clear console log history
- execute_javascript: Run JavaScript in Chrome tab
- set_breakpoint: Set debugging breakpoints
- get_chrome_debug_info: Get comprehensive debug information

CHROME DEBUGGING SETUP:
1. Install dependencies: pip install fastmcp websockets aiohttp pychrome
2. Launch Chrome with debugging: Use launch_chrome_debug() tool
3. Or manually: chrome --remote-debugging-port=9222
4. Connect to Chrome: Use connect_to_chrome() tool
5. Start monitoring: Use start_console_monitoring(tab_id) tool

EXAMPLE PROMPTS:
- "Read the package.json file in my project"
- "Show me the project structure"
- "Search for 'TODO' comments in Python files"
- "What's the git status of this repository?"
- "Analyze the code in src/main.py"
- "Launch Chrome with debugging enabled"
- "Connect to Chrome and show me the available tabs"
- "Start monitoring console logs for the first tab"
- "Get the latest console logs from Chrome"
- "Execute JavaScript: console.log('Hello from MCP!')"
""" 