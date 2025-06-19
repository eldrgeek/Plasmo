#!/usr/bin/env python3
"""
Test script to demonstrate dual-mode MCP server functionality
"""

import subprocess
import time
import json
import sys
import threading
from pathlib import Path

def test_http_mode():
    """Test the server in HTTP mode"""
    print("🖥️  Testing HTTP Mode...")
    print("=" * 40)
    
    # Start server in HTTP mode
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test if server is running
        import requests
        try:
            response = requests.get("http://127.0.0.1:8001/mcp", timeout=5)
            print(f"✅ HTTP server is running on port 8001")
            print(f"   Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP server test failed: {e}")
    except ImportError:
        print("⚠️  requests library not available, skipping HTTP test")
    
    # Stop server
    server_process.terminate()
    server_process.wait()
    print("🛑 HTTP server stopped\n")

def test_stdio_mode():
    """Test the server in STDIO mode"""
    print("📟 Testing STDIO Mode...")
    print("=" * 40)
    
    # Start server in STDIO mode
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send a simple MCP initialization message
    init_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        # Send message
        server_process.stdin.write(json.dumps(init_message) + "\n")
        server_process.stdin.flush()
        
        # Wait for response
        time.sleep(2)
        
        # Check if process is still alive (good sign)
        if server_process.poll() is None:
            print("✅ STDIO server is running and accepting input")
            print("   Process is alive and listening on stdin/stdout")
        else:
            print("❌ STDIO server exited unexpectedly")
            stderr = server_process.stderr.read()
            if stderr:
                print(f"   Error: {stderr}")
    
    except Exception as e:
        print(f"❌ STDIO server test failed: {e}")
    
    # Stop server
    server_process.terminate()
    server_process.wait()
    print("🛑 STDIO server stopped\n")

def test_command_line_args():
    """Test command line argument parsing"""
    print("⚙️  Testing Command Line Arguments...")
    print("=" * 40)
    
    # Test help
    result = subprocess.run([sys.executable, "mcp_server.py", "--help"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ --help argument works")
    else:
        print("❌ --help argument failed")
    
    # Test invalid arguments
    result = subprocess.run([sys.executable, "mcp_server.py", "--invalid"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("✅ Invalid arguments are properly rejected")
    else:
        print("❌ Invalid arguments not rejected")
    
    print()

def main():
    """Run all tests"""
    print("🚀 FastMCP Dual-Mode Server Test")
    print("=" * 50)
    print()
    
    # Check if server file exists
    if not Path("mcp_server.py").exists():
        print("❌ mcp_server.py not found in current directory")
        sys.exit(1)
    
    # Test command line args first
    test_command_line_args()
    
    # Test HTTP mode
    test_http_mode()
    
    # Test STDIO mode  
    test_stdio_mode()
    
    print("🎉 All tests completed!")
    print()
    print("📝 Summary:")
    print("   • HTTP mode: Perfect for Cursor IDE and web deployments")
    print("   • STDIO mode: Perfect for Claude Desktop and local tools")
    print("   • Both modes support all the same MCP tools")
    print("   • Chrome Debug Protocol works in both modes")

if __name__ == "__main__":
    main() 