#!/usr/bin/env python3
"""
Bootstrap Round Table Services
==============================

This script helps transition from shell-based service management 
to the new MCP-based service orchestration.

Usage:
    python bootstrap_services.py

This will:
1. Stop the current MCP server gracefully
2. Start the new MCP server with service orchestration
3. Show you how to use the new service management tools
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

def print_status(message: str, level: str = "info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[0;34m",     # Blue
        "success": "\033[0;32m",  # Green  
        "warning": "\033[1;33m",  # Yellow
        "error": "\033[0;31m",    # Red
        "reset": "\033[0m"        # Reset
    }
    
    icons = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌"
    }
    
    color = colors.get(level, colors["info"])
    icon = icons.get(level, "•")
    
    print(f"{color}{icon} {message}{colors['reset']}")

def kill_existing_mcp():
    """Kill existing MCP server processes"""
    print_status("Stopping existing MCP server processes...", "info")
    
    try:
        # Kill MCP servers
        subprocess.run(["pkill", "-f", "mcp_server.py"], capture_output=True)
        time.sleep(2)
        
        # Force kill if needed
        subprocess.run(["pkill", "-9", "-f", "mcp_server.py"], capture_output=True)
        
        print_status("Existing MCP servers stopped", "success")
        return True
    except Exception as e:
        print_status(f"Error stopping existing servers: {e}", "warning")
        return True  # Continue anyway

def start_new_mcp():
    """Start the new MCP server with service orchestration"""
    print_status("Starting new MCP server with service orchestration...", "info")
    
    try:
        # Start the MCP server
        process = subprocess.Popen([
            "python3", "packages/mcp-server/mcp_server.py", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(5)
        
        # Check if it's running
        if process.poll() is None:
            print_status(f"MCP server started successfully (PID: {process.pid})", "success")
            return process
        else:
            stdout, stderr = process.communicate()
            print_status(f"MCP server failed to start: {stderr.decode()}", "error")
            return None
            
    except Exception as e:
        print_status(f"Error starting MCP server: {e}", "error")
        return None

def test_service_tools():
    """Test the new service orchestration tools"""
    print_status("Testing service orchestration tools...", "info")
    
    try:
        import requests
        
        # Test the service_status tool
        response = requests.post(
            "http://localhost:8000/mcp/tools/service_status",
            json={},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print_status("Service orchestration tools are working!", "success")
                
                # Show summary
                summary = result.get("summary", {})
                print(f"\n📊 Service Summary:")
                print(f"   Total: {summary.get('total_services', 0)}")
                print(f"   Running: {summary.get('running', 0)}")
                print(f"   Stopped: {summary.get('stopped', 0)}")
                return True
            else:
                print_status(f"Service tools error: {result.get('error')}", "error")
                return False
        else:
            print_status(f"HTTP error: {response.status_code}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error testing service tools: {e}", "error")
        return False

def show_usage_examples():
    """Show examples of how to use the new system"""
    print(f"\n🎯 Round Table Service Management is Ready!")
    print("=" * 50)
    print("You can now manage all services through the MCP server:")
    print()
    print("📋 Check service status:")
    print("   python service_manager.py status")
    print()
    print("▶️  Start all services:")
    print("   python service_manager.py start")
    print()
    print("▶️  Start specific service:")
    print("   python service_manager.py start --service socketio_server")
    print()
    print("🛑 Stop all services:")
    print("   python service_manager.py stop")
    print()
    print("🔄 Restart a service:")
    print("   python service_manager.py restart mcp_server")
    print()
    print("📋 View service logs:")
    print("   python service_manager.py logs mcp_server")
    print()
    print("💚 Check health:")
    print("   python service_manager.py health")
    print()
    print("🔧 Or use MCP tools directly in Claude Desktop:")
    print("   service_status()")
    print("   start_service(service_name='socketio_server')")
    print("   service_health_check()")
    print()

def main():
    """Main bootstrap process"""
    print("🚀 Bootstrapping Round Table Service Orchestration")
    print("=" * 55)
    print()
    
    # Step 1: Stop existing services
    kill_existing_mcp()
    
    # Step 2: Start new MCP server
    process = start_new_mcp()
    if not process:
        print_status("Failed to start MCP server", "error")
        return 1
    
    # Step 3: Test service tools
    time.sleep(3)  # Give server time to fully initialize
    if not test_service_tools():
        print_status("Service tools are not working properly", "error")
        return 1
    
    # Step 4: Show usage examples
    show_usage_examples()
    
    print_status("Bootstrap completed successfully!", "success")
    print_status("The MCP server is running in the background", "info")
    print_status("You can now use 'python service_manager.py' to manage services", "info")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_status("\nBootstrap cancelled by user", "warning")
        sys.exit(130)
    except Exception as e:
        print_status(f"Bootstrap failed: {e}", "error")
        sys.exit(1)
