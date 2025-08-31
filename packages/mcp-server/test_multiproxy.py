#!/usr/bin/env python3
"""
Test script for Multi-Server MCP Proxy
======================================

This script demonstrates the multi-server proxy functionality including:
- Server management via manage() tool
- Health checking
- Dynamic server configuration
"""

import json
import subprocess
import time
import sys
from typing import Dict, Any

def run_proxy_command(servers: str = "main=http://localhost:8000/mcp", debug: bool = True) -> subprocess.Popen:
    """Start the proxy with given configuration"""
    cmd = [
        sys.executable, 
        "packages/mcp-server/mcp_proxy.py",
        "--stdio",
        "--servers", servers
    ]
    
    if debug:
        cmd.append("--debug")
    
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def send_mcp_request(proxy_process: subprocess.Popen, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send an MCP request to the proxy"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    request_str = json.dumps(request) + "\n"
    proxy_process.stdin.write(request_str)
    proxy_process.stdin.flush()
    
    # Read response
    response_line = proxy_process.stdout.readline()
    if response_line:
        try:
            return json.loads(response_line)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse response: {e}", "raw": response_line}
    
    return {"error": "No response received"}

def test_proxy_functionality():
    """Test the multi-server proxy functionality"""
    
    print("🚀 Testing Multi-Server MCP Proxy")
    print("=" * 50)
    
    # Start proxy with initial server
    print("\n1. Starting proxy with initial server...")
    proxy = run_proxy_command("main=http://localhost:8000/mcp")
    
    # Give it time to start
    time.sleep(2)
    
    # Test initialization request
    print("\n2. Sending initialization request...")
    init_response = send_mcp_request(proxy, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    })
    
    print(f"   Init response: {init_response}")
    
    # Test listing tools
    print("\n3. Listing available tools...")
    tools_response = send_mcp_request(proxy, "tools/list")
    print(f"   Tools response: {tools_response}")
    
    # Test manage tool - list servers
    print("\n4. Testing manage tool - list servers...")
    manage_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {"operation": "list"}
    })
    print(f"   Manage list response: {manage_response}")
    
    # Test manage tool - add server
    print("\n5. Testing manage tool - add server...")
    add_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {
            "operation": "add",
            "name": "backup",
            "url": "http://localhost:8001/mcp"
        }
    })
    print(f"   Add server response: {add_response}")
    
    # Test manage tool - list servers again
    print("\n6. Testing manage tool - list servers after adding...")
    manage_response2 = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {"operation": "list"}
    })
    print(f"   Manage list response: {manage_response2}")
    
    # Test proxy status
    print("\n7. Testing proxy status...")
    status_response = send_mcp_request(proxy, "tools/call", {
        "name": "proxy_status",
        "arguments": {}
    })
    print(f"   Proxy status response: {status_response}")
    
    # Test health check
    print("\n8. Testing health check...")
    health_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {
            "operation": "health",
            "name": "all"
        }
    })
    print(f"   Health check response: {health_response}")
    
    # Test remove server
    print("\n9. Testing manage tool - remove server...")
    remove_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {
            "operation": "remove",
            "name": "backup"
        }
    })
    print(f"   Remove server response: {remove_response}")
    
    # Cleanup
    print("\n10. Cleaning up...")
    proxy.terminate()
    proxy.wait()
    
    print("\n✅ Multi-server proxy test completed!")

def test_command_line_configuration():
    """Test command line server configuration"""
    
    print("\n🔧 Testing Command Line Configuration")
    print("=" * 50)
    
    # Test multiple servers from command line
    print("\n1. Starting proxy with multiple servers...")
    servers_config = "main=http://localhost:8000/mcp,backup=http://localhost:8001/mcp,test=http://localhost:8002/mcp"
    
    proxy = run_proxy_command(servers_config)
    time.sleep(2)
    
    # Initialize
    init_response = send_mcp_request(proxy, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    })
    
    # List servers
    print("\n2. Listing configured servers...")
    manage_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {"operation": "list"}
    })
    print(f"   Server list: {manage_response}")
    
    # Test disable/enable
    print("\n3. Testing disable/enable server...")
    disable_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {
            "operation": "disable",
            "name": "backup"
        }
    })
    print(f"   Disable response: {disable_response}")
    
    enable_response = send_mcp_request(proxy, "tools/call", {
        "name": "manage",
        "arguments": {
            "operation": "enable",
            "name": "backup"
        }
    })
    print(f"   Enable response: {enable_response}")
    
    # Cleanup
    proxy.terminate()
    proxy.wait()
    
    print("\n✅ Command line configuration test completed!")

def main():
    """Main test function"""
    print("Multi-Server MCP Proxy Test Suite")
    print("=" * 60)
    
    try:
        test_proxy_functionality()
        test_command_line_configuration()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 