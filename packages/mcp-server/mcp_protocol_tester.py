#!/usr/bin/env python3
"""
MCP Protocol Test Suite
======================

Tests the MCP server through the actual MCP protocol using stdio communication.
This ensures the server works correctly when integrated with tools like Claude Desktop.

Usage:
    python mcp_protocol_tester.py              # Run all tests
    python mcp_protocol_tester.py --verbose    # Verbose output
    python mcp_protocol_tester.py --mode=proxy # Test against proxy instead of direct server
    python mcp_protocol_tester.py --test=read_file # Run specific test
"""

import asyncio
import json
import os
import subprocess
import tempfile
import time
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import signal
import atexit
from datetime import datetime


class MCPProtocolTester:
    """Test MCP server through actual MCP protocol."""
    
    def __init__(self, verbose=False, mode="direct", server_path=None):
        self.verbose = verbose
        self.mode = mode  # "direct" or "proxy"
        self.test_results = {}
        self.server_process = None
        self.server_path = server_path or "mcp_server.py"
        
        # Test data - use subdirectory in current project
        self.temp_dir = os.path.join(os.getcwd(), "test_temp_mcp")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.test_files = {}
        
        # Available test methods
        self.available_tests = {
            "initialization": self.test_server_initialization,
            "list_tools": self.test_list_tools,
            "read_file": self.test_read_file,
            "write_file": self.test_write_file,
            "file_operations": self.test_file_operations,
            "system_operations": self.test_system_operations,
            "code_analysis": self.test_code_analysis,
        }
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.log("Received shutdown signal, cleaning up...", "INFO")
        self.cleanup()
        sys.exit(0)
        
    def cleanup(self):
        """Clean up resources."""
        self.stop_mcp_server()
        self.cleanup_test_environment()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        if self.verbose or level in ["ERROR", "FAIL", "PASS", "WARN"]:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def setup_test_environment(self):
        """Set up test files and data."""
        self.log("Setting up test environment...")
        
        # Create test files
        test_files = {
            "test.txt": "Hello, MCP Protocol!\nThis is a test file for MCP testing.",
            "test.json": '{"name": "mcp_test", "value": 42, "protocol": "mcp"}',
            "test.py": '''#!/usr/bin/env python3
"""Test Python file for MCP analysis."""

def hello_mcp():
    """Say hello to MCP."""
    print("Hello, MCP Protocol!")
    return "Hello MCP"

class MCPTestClass:
    """A test class for MCP."""
    
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello from MCP, {self.name}!"

if __name__ == "__main__":
    hello_mcp()
''',
            "unicode_test.txt": "MCP Unicode test: 🚀 🎉 👋 \n中文MCP测试\nMCP Emoji: 😀😎🔥"
        }
        
        for filename, content in test_files.items():
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.test_files[filename] = str(file_path)
        
        self.log(f"Created test files in: {self.temp_dir}")
    
    def cleanup_test_environment(self):
        """Clean up test files."""
        self.log("Cleaning up test environment...")
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def start_mcp_server(self):
        """Start MCP server in stdio mode."""
        server_script = "mcp_testing_proxy.py" if self.mode == "proxy" else self.server_path
        self.log(f"Starting MCP server in stdio mode (mode: {self.mode})...")
        self.log(f"Server script: {server_script}")
        
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, server_script, "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            self.log("MCP server started successfully")
            time.sleep(2)  # Give server time to initialize
            return True
        except Exception as e:
            self.log(f"Failed to start MCP server: {e}", "ERROR")
            return False
    
    def stop_mcp_server(self):
        """Stop MCP server."""
        if self.server_process:
            self.log("Stopping MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
    
    def send_mcp_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send MCP request and get response."""
        if not self.server_process:
            return {"error": "MCP server not running"}
        
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000000) % 1000000,  # Use timestamp as ID
            "method": method
        }
        
        if params:
            request["params"] = params
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.log(f"Sending MCP request: {method}")
            if self.verbose:
                self.log(f"Request data: {request_json.strip()}")
            
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if not response_line:
                return {"error": "No response from server"}
            
            response = json.loads(response_line.strip())
            if self.verbose:
                self.log(f"Response: {json.dumps(response, indent=2)}")
            
            return response
            
        except Exception as e:
            self.log(f"MCP request failed: {e}", "ERROR")
            return {"error": str(e)}
    
    def test_server_initialization(self) -> Dict[str, Any]:
        """Test server initialization and basic communication."""
        self.log("Testing server initialization...")
        
        # Test initialize method
        response = self.send_mcp_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "mcp-test-client",
                "version": "1.0.0"
            }
        })
        
        if "result" in response:
            self.log("  Server initialization: PASS", "PASS")
            
            # Send initialized notification
            self.send_mcp_request("notifications/initialized")
            
            return {"initialization": {"status": "PASS", "message": "Server initialized successfully"}}
        else:
            self.log("  Server initialization: FAIL", "FAIL")
            return {"initialization": {"status": "FAIL", "message": f"Initialization failed: {response}"}}
    
    def test_list_tools(self) -> Dict[str, Any]:
        """Test tools/list method."""
        self.log("Testing tools/list...")
        
        response = self.send_mcp_request("tools/list", {})
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            tool_count = len(tools)
            self.log(f"  Found {tool_count} tools: PASS", "PASS")
            
            # Log tool names for reference
            tool_names = [tool.get("name", "unnamed") for tool in tools]
            self.log(f"  Available tools: {', '.join(tool_names)}")
            
            return {"list_tools": {"status": "PASS", "message": f"Found {tool_count} tools", "tools": tool_names}}
        else:
            self.log("  tools/list: FAIL", "FAIL")
            return {"list_tools": {"status": "FAIL", "message": f"Failed to list tools: {response}"}}
    
    def test_read_file(self) -> Dict[str, Any]:
        """Test read_file tool."""
        self.log("  Testing read_file...")
        response = self.send_mcp_request("tools/call", {
            "name": "read_file",
            "arguments": {
                "file_path": self.test_files["test.txt"]
            }
        })
        
        if ("result" in response and 
            "content" in response["result"] and 
            "Hello, MCP Protocol!" in str(response["result"]["content"])):
            self.log("    read_file: PASS", "PASS")
            return {"status": "PASS", "message": "Successfully read file through MCP"}
        else:
            self.log("    read_file: FAIL", "FAIL")
            return {"status": "FAIL", "message": f"Failed to read file: {response}"}
    
    def test_write_file(self) -> Dict[str, Any]:
        """Test write_file tool."""
        self.log("  Testing write_file...")
        test_content = "MCP Protocol Write Test\nLine 2 from MCP"
        write_file_path = str(Path(self.temp_dir) / "mcp_write_test.txt")
        
        response = self.send_mcp_request("tools/call", {
            "name": "write_file", 
            "arguments": {
                "file_path": write_file_path,
                "content": test_content
            }
        })
        
        if "result" in response and response["result"].get("success"):
            # Verify the file was actually written
            if os.path.exists(write_file_path):
                with open(write_file_path, 'r') as f:
                    written_content = f.read()
                if test_content in written_content:
                    self.log("    write_file: PASS", "PASS")
                    return {"status": "PASS", "message": "Successfully wrote file through MCP"}
            
        self.log("    write_file: FAIL", "FAIL")
        return {"status": "FAIL", "message": f"Failed to write file: {response}"}
    
    def test_file_operations(self) -> Dict[str, Any]:
        """Test file operation tools through MCP protocol."""
        self.log("Testing file operations through MCP...")
        results = {}
        
        results["read_file"] = self.test_read_file()
        results["write_file"] = self.test_write_file()
        
        return results
    
    def test_system_operations(self) -> Dict[str, Any]:
        """Test system operation tools through MCP protocol."""
        self.log("Testing system operations through MCP...")
        results = {}
        
        # Test get_system_info
        self.log("  Testing get_system_info...")
        response = self.send_mcp_request("tools/call", {
            "name": "get_system_info",
            "arguments": {
                "include_sensitive": False
            }
        })
        
        if ("result" in response and 
            "content" in response["result"] and 
            "platform" in str(response["result"]["content"])):
            results["get_system_info"] = {"status": "PASS", "message": "Successfully got system info through MCP"}
            self.log("    get_system_info: PASS", "PASS")
        else:
            results["get_system_info"] = {"status": "FAIL", "message": f"Failed to get system info: {response}"}
            self.log("    get_system_info: FAIL", "FAIL")
        
        # Test server_info
        self.log("  Testing server_info...")
        response = self.send_mcp_request("tools/call", {
            "name": "server_info",
            "arguments": {}
        })
        
        if ("result" in response and 
            "content" in response["result"]):
            results["server_info"] = {"status": "PASS", "message": "Successfully got server info through MCP"}
            self.log("    server_info: PASS", "PASS")
        else:
            results["server_info"] = {"status": "FAIL", "message": f"Failed to get server info: {response}"}
            self.log("    server_info: FAIL", "FAIL")
        
        return results
    
    def test_code_analysis(self) -> Dict[str, Any]:
        """Test code analysis through MCP protocol."""
        self.log("Testing code analysis through MCP...")
        results = {}
        
        # Test analyze_code
        self.log("  Testing analyze_code...")
        response = self.send_mcp_request("tools/call", {
            "name": "analyze_code",
            "arguments": {
                "file_path": self.test_files["test.py"]
            }
        })
        
        if ("result" in response and 
            "content" in response["result"]):
            results["analyze_code"] = {"status": "PASS", "message": "Successfully analyzed code through MCP"}
            self.log("    analyze_code: PASS", "PASS")
        else:
            results["analyze_code"] = {"status": "FAIL", "message": f"Failed to analyze code: {response}"}
            self.log("    analyze_code: FAIL", "FAIL")
        
        return results
    
    def run_single_test(self, test_name: str) -> Dict[str, Any]:
        """Run a single test by name."""
        if test_name not in self.available_tests:
            return {"error": f"Unknown test: {test_name}. Available tests: {list(self.available_tests.keys())}"}
        
        self.log(f"🧪 Running single test: {test_name}")
        self.log("=" * 50)
        
        start_time = time.time()
        
        try:
            # Setup
            self.setup_test_environment()
            
            # Start MCP server
            if not self.start_mcp_server():
                return {"error": "Failed to start MCP server"}
            
            # Run the specific test
            test_func = self.available_tests[test_name]
            result = test_func()
            
        except Exception as e:
            self.log(f"Test execution error: {e}", "ERROR")
            result = {"error": str(e)}
        
        finally:
            # Cleanup
            self.cleanup()
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("=" * 50)
        self.log(f"🏁 Test '{test_name}' completed in {duration:.2f} seconds")
        
        return {test_name: result}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all MCP protocol tests."""
        self.log(f"🚀 Starting MCP Protocol Test Suite (mode: {self.mode})")
        self.log("=" * 50)
        
        start_time = time.time()
        all_results = {}
        
        try:
            # Setup
            self.setup_test_environment()
            
            # Start MCP server
            if not self.start_mcp_server():
                return {"error": "Failed to start MCP server"}
            
            # Run tests in order
            all_results.update(self.test_server_initialization())
            all_results.update(self.test_list_tools())
            all_results.update(self.test_file_operations())
            all_results.update(self.test_system_operations())
            all_results.update(self.test_code_analysis())
            
        except Exception as e:
            self.log(f"Test execution error: {e}", "ERROR")
            all_results["error"] = str(e)
        
        finally:
            # Cleanup
            self.cleanup()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary
        total_tests = len([k for k in all_results.keys() if k != "error"])
        passed_tests = sum(1 for result in all_results.values() 
                          if isinstance(result, dict) and result.get("status") == "PASS")
        failed_tests = total_tests - passed_tests
        
        self.log("=" * 50)
        self.log(f"🏁 MCP Protocol Test Summary (mode: {self.mode})")
        self.log(f"📊 Total Tests: {total_tests}")
        self.log(f"✅ Passed: {passed_tests}")
        self.log(f"❌ Failed: {failed_tests}")
        self.log(f"⏱️  Duration: {duration:.2f} seconds")
        
        if passed_tests == total_tests and total_tests > 0:
            self.log("🎉 All tests passed!", "PASS")
        else:
            self.log(f"⚠️  {failed_tests} test(s) failed", "FAIL")
        
        # Add summary to results
        all_results["_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "duration": duration,
            "mode": self.mode,
            "timestamp": datetime.now().isoformat()
        }
        
        return all_results


def main():
    """Main entry point for MCP protocol tester."""
    parser = argparse.ArgumentParser(description="MCP Protocol Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--mode", choices=["direct", "proxy"], default="direct",
                       help="Test mode: direct server or through proxy")
    parser.add_argument("--test", help="Run specific test by name")
    parser.add_argument("--server-path", default="mcp_server.py",
                       help="Path to MCP server script")
    parser.add_argument("--list-tests", action="store_true",
                       help="List available tests")
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = MCPProtocolTester(
        verbose=args.verbose, 
        mode=args.mode,
        server_path=args.server_path
    )
    
    # List tests if requested
    if args.list_tests:
        print("Available tests:")
        for test_name in tester.available_tests.keys():
            print(f"  - {test_name}")
        return
    
    # Run tests
    if args.test:
        results = tester.run_single_test(args.test)
    else:
        results = tester.run_all_tests()
    
    # Exit with appropriate code
    if "error" in results:
        sys.exit(1)
    elif "_summary" in results:
        summary = results["_summary"]
        sys.exit(0 if summary["failed_tests"] == 0 else 1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 