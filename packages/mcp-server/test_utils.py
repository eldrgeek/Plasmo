#!/usr/bin/env python3
"""
Test Utilities for MCP Server Testing
=====================================

Common utilities for all test suites including server detection,
real implementation testing, and test environment setup.
"""

import requests
import time
import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def check_server_health(url: str = "http://localhost:8000", timeout: int = 2) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if MCP server is running and healthy.
    
    Args:
        url: Server URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (is_healthy, server_info)
    """
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            try:
                data = response.json()
                return True, data
            except:
                return True, {"status": "healthy", "message": "Server responding"}
        return False, None
    except requests.exceptions.ConnectionError:
        return False, None
    except requests.exceptions.Timeout:
        return False, None
    except Exception as e:
        logger.debug(f"Health check failed: {e}")
        return False, None


def ensure_server_running(preferred_url: str = "http://localhost:8001", 
                         fallback_url: str = "http://localhost:8000",
                         start_if_needed: bool = True) -> Optional[str]:
    """
    Ensure MCP server is running, either by finding existing instance or starting new one.
    
    Args:
        preferred_url: Primary server URL to check
        fallback_url: Fallback URL (e.g., proxy) to check
        start_if_needed: Whether to start server if not running
        
    Returns:
        Server URL if available, None if server cannot be started
    """
    # Check preferred URL
    is_healthy, info = check_server_health(preferred_url)
    if is_healthy:
        logger.info(f"✅ Found running MCP server at {preferred_url}")
        if info:
            logger.info(f"   Server info: {info.get('status', 'unknown')}")
        return preferred_url
    
    # Check fallback URL (proxy)
    is_healthy, info = check_server_health(fallback_url)
    if is_healthy:
        logger.info(f"✅ Found running MCP proxy server at {fallback_url}")
        if info:
            logger.info(f"   Proxy info: {info.get('status', 'unknown')}")
        return fallback_url
    
    # Start server if needed
    if start_if_needed:
        logger.info("🚀 No running server found, starting MCP server...")
        server_process = start_mcp_server()
        if server_process:
            # Wait for server to be ready
            for i in range(10):  # 10 second timeout
                time.sleep(1)
                is_healthy, _ = check_server_health(preferred_url)
                if is_healthy:
                    logger.info(f"✅ MCP server started successfully at {preferred_url}")
                    return preferred_url
            
            logger.error("❌ Server started but not responding to health checks")
            server_process.terminate()
        else:
            logger.error("❌ Failed to start MCP server")
    
    return None


def start_mcp_server() -> Optional[subprocess.Popen]:
    """
    Start MCP server as subprocess.
    
    Returns:
        Subprocess object if started successfully, None otherwise
    """
    try:
        server_script = Path(__file__).parent / "mcp_server.py"
        if not server_script.exists():
            logger.error(f"Server script not found: {server_script}")
            return None
        
        # Start server
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
        )
        
        # Check if process started
        time.sleep(0.5)
        if process.poll() is None:
            return process
        else:
            stdout, stderr = process.communicate(timeout=1)
            logger.error(f"Server failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"Exception starting server: {e}")
        return None


# Global session management
_mcp_session_id = None
_mcp_session_lock = None
_mcp_session_initialized = False

def get_or_create_session_id(server_url: str) -> Optional[str]:
    """Get existing session ID or create a new one with proper MCP initialization."""
    global _mcp_session_id, _mcp_session_lock, _mcp_session_initialized
    
    if _mcp_session_lock is None:
        import threading
        _mcp_session_lock = threading.Lock()
    
    with _mcp_session_lock:
        if _mcp_session_id and _mcp_session_initialized:
            return _mcp_session_id
        
        # Initialize MCP session properly
        endpoint_url = f"{server_url.rstrip('/')}/mcp/"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Send proper MCP initialization
        init_payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            response = requests.post(endpoint_url, json=init_payload, headers=headers, timeout=10)
            session_id = response.headers.get("mcp-session-id")
            if session_id and response.status_code == 200:
                _mcp_session_id = session_id
                _mcp_session_initialized = True
                logger.info(f"Initialized MCP session: {session_id[:16]}...")
                return session_id
            else:
                logger.error(f"MCP initialization failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"Could not initialize MCP session: {e}")
        
        return None

def make_mcp_request(server_url: str, method: str, params: Dict[str, Any] = None, 
                     timeout: int = 30) -> Dict[str, Any]:
    """
    Make a real MCP JSON-RPC request to the server.
    
    Args:
        server_url: MCP server URL
        method: MCP method name (e.g., 'tools/call')
        params: Method parameters
        timeout: Request timeout
        
    Returns:
        Response data or error dict
    """
    import time
    
    # Get session ID
    session_id = get_or_create_session_id(server_url)
    
    request_id = int(time.time() * 1000000) % 1000000  # Integer ID required
    
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"  # Required for FastMCP
    }
    
    # Add session ID to headers if available
    if session_id:
        headers["MCP-Session-ID"] = session_id
    
    # Use /mcp/ endpoint for FastMCP streamable-http transport
    endpoint_url = f"{server_url.rstrip('/')}/mcp/"
    
    try:
        response = requests.post(
            endpoint_url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        # Update session ID if provided in response
        new_session_id = response.headers.get("mcp-session-id")
        if new_session_id and new_session_id != session_id:
            global _mcp_session_id
            _mcp_session_id = new_session_id
            logger.debug(f"Updated session ID: {new_session_id[:16]}...")
        
        if response.status_code == 200:
            # Handle SSE format if needed
            if response.headers.get("content-type", "").startswith("text/event-stream"):
                return parse_sse_response(response.text)
            else:
                return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text,
                "status_code": response.status_code,
                "url": endpoint_url,
                "session_id": session_id
            }
            
    except requests.exceptions.Timeout:
        return {"error": "Request timeout", "timeout": timeout}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def parse_sse_response(text: str) -> Dict[str, Any]:
    """Parse Server-Sent Events response format."""
    lines = text.strip().split('\n')
    for line in lines:
        if line.startswith('data: '):
            try:
                return json.loads(line[6:])
            except json.JSONDecodeError:
                pass
    return {"error": "Failed to parse SSE response", "raw": text}


def call_mcp_tool(server_url: str, tool_name: str, arguments: Dict[str, Any] = None,
                  timeout: int = 30) -> Dict[str, Any]:
    """
    Call an MCP tool using real server implementation.
    
    Args:
        server_url: MCP server URL
        tool_name: Name of the tool to call
        arguments: Tool arguments
        timeout: Request timeout
        
    Returns:
        Tool response or error dict
    """
    # Standard MCP protocol: tools/call with name and arguments
    params = {
        "name": tool_name,
        "arguments": arguments or {}
    }
    
    response = make_mcp_request(server_url, "tools/call", params, timeout)
    
    # Extract result from response
    if "result" in response:
        return response["result"]
    elif "error" in response:
        return {"success": False, "error": response["error"]}
    else:
        return response


def setup_test_environment(test_name: str) -> Dict[str, Any]:
    """
    Setup test environment with server URL and test directory.
    
    Args:
        test_name: Name of the test suite
        
    Returns:
        Dict with server_url, test_dir, and other test configuration
    """
    import tempfile
    
    # Ensure server is running
    server_url = ensure_server_running()
    if not server_url:
        raise RuntimeError("Could not start or connect to MCP server")
    
    # Create test directory
    test_dir = Path(tempfile.mkdtemp(prefix=f"mcp_test_{test_name}_"))
    
    # Get current working directory for context
    original_cwd = os.getcwd()
    
    return {
        "server_url": server_url,
        "test_dir": test_dir,
        "original_cwd": original_cwd,
        "test_name": test_name,
        "start_time": time.time()
    }


def cleanup_test_environment(env: Dict[str, Any]):
    """
    Cleanup test environment.
    
    Args:
        env: Environment dict from setup_test_environment
    """
    import shutil
    
    # Remove test directory
    if "test_dir" in env and env["test_dir"].exists():
        try:
            shutil.rmtree(env["test_dir"])
        except:
            pass
    
    # Log test duration
    if "start_time" in env:
        duration = time.time() - env["start_time"]
        logger.info(f"Test '{env.get('test_name', 'unknown')}' completed in {duration:.2f}s")


# Convenience function for backwards compatibility
def get_test_server_url() -> str:
    """Get URL of running MCP server, starting if needed."""
    url = ensure_server_running()
    if not url:
        raise RuntimeError("MCP server not available")
    return url