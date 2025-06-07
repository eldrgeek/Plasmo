# Add this to mcp_server.py to add version tracking and better debugging

import time
from datetime import datetime

# Version information
SERVER_VERSION = "1.0.1"
SERVER_BUILD_TIME = datetime.now().isoformat()
LAST_UPDATED = "2025-06-06 Claude Debug Session"

@mcp.tool()
def mcp_server_version() -> Dict[str, Any]:
    """
    Get detailed version information about this MCP server to track updates.
    
    Returns:
        Detailed version and status information
    """
    # Get tools by calling the list_tools method
    tools_list = []
    try:
        # Get all tool names from the server
        tools_list = list(mcp.tools.keys()) if hasattr(mcp, 'tools') else []
    except:
        tools_list = []
    
    return {
        "server_name": "Cursor Development Assistant",
        "version": SERVER_VERSION,
        "build_time": SERVER_BUILD_TIME,
        "last_updated": LAST_UPDATED,
        "description": "MCP server providing development tools for Cursor IDE with Chrome Debug Protocol",
        "transport": "HTTP",
        "tools_count": len(tools_list),
        "available_tools": tools_list,
        "chrome_debug_support": True,
        "chrome_debug_port": CHROME_DEBUG_PORT,
        "connection_status": {
            "chrome_instances": len(chrome_instances),
            "active_listeners": len(console_log_listeners),
            "total_console_logs": len(console_logs)
        },
        "current_time": datetime.now().isoformat(),
        "issues_identified": [
            "JavaScript execution receives WebSocket events instead of responses",
            "Console monitoring doesn't capture real-time logs",
            "Need proper async WebSocket handling with request/response correlation"
        ],
        "recommended_action": "Use the fixed version in mcp_server_fixed.py for proper Chrome debugging"
    }

# Quick test function for JavaScript execution
@mcp.tool()
def test_javascript_execution(tab_id: str, connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Test JavaScript execution and diagnose issues.
    
    Args:
        tab_id: Chrome tab ID to test with
        connection_id: Chrome connection identifier
        
    Returns:
        Test results and diagnostics
    """
    try:
        if connection_id not in chrome_instances:
            return {"error": "Not connected to Chrome. Use connect_to_chrome first."}
        
        # Test with simple console.log
        test_code = "console.log('🧪 MCP Test:', new Date().toISOString()); return 'test_completed';"
        
        result = execute_javascript(test_code, tab_id, connection_id)
        
        return {
            "test_code": test_code,
            "execution_result": result,
            "analysis": {
                "javascript_execution_working": result.get("success", False),
                "common_issue": "WebSocket receiving events instead of command responses",
                "recommendation": "Use mcp_server_fixed.py for proper implementation"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "test_failed": True,
            "timestamp": datetime.now().isoformat()
        }

# Console log inspection
@mcp.tool() 
def inspect_console_monitoring(tab_id: str, connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Inspect the current state of console monitoring for a tab.
    
    Args:
        tab_id: Chrome tab ID to inspect
        connection_id: Chrome connection identifier
        
    Returns:
        Console monitoring status and diagnostics
    """
    try:
        listener_key = f"{connection_id}:{tab_id}"
        
        # Check if monitoring is set up
        monitoring_active = listener_key in console_log_listeners
        log_count = len(console_log_listeners.get(listener_key, []))
        
        # Get recent logs
        recent_logs = console_log_listeners.get(listener_key, [])[-5:] if monitoring_active else []
        
        return {
            "tab_id": str(tab_id),
            "connection_id": str(connection_id),
            "listener_key": listener_key,
            "monitoring_active": monitoring_active,
            "log_count": log_count,
            "recent_logs": recent_logs,
            "global_log_count": len(console_logs),
            "total_listeners": len(console_log_listeners),
            "diagnosis": {
                "issue": "Current implementation only logs setup messages, not real console output",
                "reason": "No persistent WebSocket connection to capture Runtime.consoleAPICalled events",
                "solution": "Use mcp_server_fixed.py which implements real-time WebSocket monitoring"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
