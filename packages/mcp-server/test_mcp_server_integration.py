#!/usr/bin/env python3
"""
MCP Server Integration Tests
============================

This test suite provides comprehensive integration testing for the MCP server,
testing all tools against the actual running server instance.

Usage:
    python test_mcp_server_integration.py
    python test_mcp_server_integration.py --verbose
"""

import asyncio
import aiohttp
import json
import sys
import time
import tempfile
import subprocess
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerIntegrationTester:
    """Integration tester for MCP server."""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8001"):
        self.server_url = server_url
        self.mcp_endpoint = f"{server_url}/mcp"
        self.health_endpoint = f"{server_url}/health"
        self.test_results = []
        self.session_id = None
        self.session = None
        
    async def start_session(self):
        """Start HTTP session for testing."""
        self.session = aiohttp.ClientSession()
        
    async def stop_session(self):
        """Stop HTTP session."""
        if self.session:
            await self.session.close()
    
    async def check_server_health(self) -> bool:
        """Check if server is healthy."""
        try:
            async with self.session.get(self.health_endpoint) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def initialize_mcp_session(self) -> bool:
        """Initialize MCP session."""
        try:
            # Initialize session
            init_request = {
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "integration-tester",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with self.session.post(self.mcp_endpoint, json=init_request) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ MCP session initialized")
                    return True
                else:
                    logger.error(f"❌ MCP initialization failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ MCP session initialization error: {e}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        try:
            request = {
                "method": "tools/list",
                "params": {}
            }
            
            async with self.session.post(self.mcp_endpoint, json=request) as response:
                if response.status == 200:
                    result = await response.json()
                    tools = result.get("result", {}).get("tools", [])
                    logger.info(f"✅ Listed {len(tools)} tools")
                    return tools
                else:
                    logger.error(f"❌ Failed to list tools: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error listing tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific tool."""
        try:
            request = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                }
            }
            
            async with self.session.post(self.mcp_endpoint, json=request) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Tool call failed for {tool_name}: {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}", "details": error_text}
                    
        except Exception as e:
            logger.error(f"❌ Error calling tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def test_tool(self, tool_name: str, arguments: Dict[str, Any] = None, 
                       expected_keys: List[str] = None) -> Dict[str, Any]:
        """Test a specific tool and validate response."""
        logger.info(f"🧪 Testing tool: {tool_name}")
        
        start_time = time.time()
        result = await self.call_tool(tool_name, arguments)
        end_time = time.time()
        
        test_result = {
            "tool_name": tool_name,
            "execution_time": round(end_time - start_time, 3),
            "success": "error" not in result,
            "result": result
        }
        
        # Validate expected keys
        if expected_keys and test_result["success"]:
            for key in expected_keys:
                if key not in result:
                    test_result["success"] = False
                    test_result["error"] = f"Missing expected key: {key}"
                    break
        
        status = "✅" if test_result["success"] else "❌"
        logger.info(f"{status} {tool_name} - {test_result['execution_time']}s")
        
        self.test_results.append(test_result)
        return test_result
    
    async def test_system_tools(self):
        """Test system information tools."""
        logger.info("🔧 Testing System Tools")
        
        # Test health endpoint
        await self.test_tool("health")
        
        # Test server info
        await self.test_tool("server_info")
        
        # Test system info
        await self.test_tool("get_system_info")
        
        # Test system info with sensitive data
        await self.test_tool("get_system_info", {"include_sensitive": True})
        
        # Test project structure
        await self.test_tool("get_project_structure", {"directory": ".", "max_depth": 2})
    
    async def test_agent_tools(self):
        """Test agent management tools."""
        logger.info("👥 Testing Agent Tools")
        
        # Test agent registration
        await self.test_tool("register_agent_with_name", {"agent_name": "test_agent"})
        
        # Test getting current agent name
        await self.test_tool("get_current_agent_name")
        
        # Test messaging operations
        await self.test_tool("messages", {
            "operation": "send",
            "payload": {
                "to": "test_target",
                "subject": "Test Message",
                "message": "Hello from integration test"
            }
        })
        
        # Test getting messages
        await self.test_tool("messages", {
            "operation": "get",
            "payload": {}
        })
        
        # Test notifications
        await self.test_tool("notify", {
            "operation": "notify",
            "target_agent": "test_agent",
            "message": "Test notification"
        })
    
    async def test_file_tools(self):
        """Test file operation tools."""
        logger.info("📁 Testing File Tools")
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file content")
            temp_file = f.name
        
        try:
            # Test smart read file
            await self.test_tool("smart_read_file", {"file_path": temp_file})
            
            # Test smart write file
            await self.test_tool("smart_write_file", {
                "file_path": temp_file,
                "content": "Updated content",
                "mode": "overwrite"
            })
            
            # Test smart edit file
            await self.test_tool("smart_edit_file", {
                "file_path": temp_file,
                "operation": "replace_line",
                "line_number": 1,
                "content": "Edited content"
            })
            
            # Test code analysis
            await self.test_tool("analyze_code", {"file_path": temp_file})
            
        finally:
            # Clean up
            Path(temp_file).unlink(missing_ok=True)
    
    async def test_chrome_tools(self):
        """Test Chrome Debug Protocol tools."""
        logger.info("🌐 Testing Chrome Tools")
        
        # Test Chrome connection (may fail if Chrome not running)
        await self.test_tool("connect_to_chrome", {"port": 9222})
        
        # Test getting Chrome tabs
        await self.test_tool("get_chrome_tabs")
        
        # Test Chrome debug launch
        await self.test_tool("launch_chrome_debug")
    
    async def test_service_tools(self):
        """Test service orchestration tools."""
        logger.info("⚙️ Testing Service Tools")
        
        # Test service status
        await self.test_tool("service_status")
        
        # Test service health check
        await self.test_tool("service_health_check")
        
        # Test service logs (may fail if no services)
        await self.test_tool("service_logs", {"service_name": "test_service", "lines": 10})
    
    async def test_firebase_tools(self):
        """Test Firebase tools."""
        logger.info("🔥 Testing Firebase Tools")
        
        # Test Firebase project status (may fail without credentials)
        await self.test_tool("firebase_project_status", {"project_id": "test-project"})
    
    async def test_error_handling(self):
        """Test error handling and recovery."""
        logger.info("🔧 Testing Error Handling")
        
        # Test invalid tool call
        result = await self.call_tool("nonexistent_tool")
        self.test_results.append({
            "tool_name": "nonexistent_tool",
            "execution_time": 0,
            "success": "error" in result,
            "result": result,
            "test_type": "error_handling"
        })
        
        # Test invalid parameters
        result = await self.call_tool("smart_read_file", {"invalid_param": "value"})
        self.test_results.append({
            "tool_name": "smart_read_file_invalid_params",
            "execution_time": 0,
            "success": "error" in result,
            "result": result,
            "test_type": "error_handling"
        })
        
        # Test get last errors
        await self.test_tool("get_last_errors", {"limit": 10})
    
    async def test_performance(self):
        """Test performance characteristics."""
        logger.info("⚡ Testing Performance")
        
        # Test rapid tool calls
        start_time = time.time()
        tasks = []
        for i in range(10):
            tasks.append(self.call_tool("health"))
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / len(results)
        
        self.test_results.append({
            "tool_name": "performance_test",
            "execution_time": round(total_time, 3),
            "success": all("error" not in result for result in results),
            "result": {
                "total_calls": len(results),
                "total_time": round(total_time, 3),
                "average_time": round(avg_time, 3),
                "calls_per_second": round(len(results) / total_time, 2)
            },
            "test_type": "performance"
        })
        
        logger.info(f"⚡ Performance: {len(results)} calls in {total_time:.3f}s ({avg_time:.3f}s avg)")
    
    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("🚀 Starting MCP Server Integration Tests")
        
        # Start session
        await self.start_session()
        
        try:
            # Check server health
            if not await self.check_server_health():
                logger.error("❌ Server is not healthy, aborting tests")
                return False
            
            # Initialize MCP session
            if not await self.initialize_mcp_session():
                logger.error("❌ Failed to initialize MCP session")
                return False
            
            # List available tools
            tools = await self.list_tools()
            logger.info(f"📋 Found {len(tools)} tools: {[t['name'] for t in tools[:10]]}")
            
            # Run test suites
            await self.test_system_tools()
            await self.test_agent_tools()
            await self.test_file_tools()
            await self.test_chrome_tools()
            await self.test_service_tools()
            await self.test_firebase_tools()
            await self.test_error_handling()
            await self.test_performance()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
        finally:
            await self.stop_session()
    
    def print_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 80)
        print("🎯 MCP Server Integration Test Results")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 Summary:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {(successful_tests / total_tests * 100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['tool_name']}: {result.get('error', 'Unknown error')}")
        
        print(f"\n⚡ Performance Metrics:")
        execution_times = [r["execution_time"] for r in self.test_results if r["execution_time"] > 0]
        if execution_times:
            print(f"   • Average execution time: {sum(execution_times) / len(execution_times):.3f}s")
            print(f"   • Fastest tool: {min(execution_times):.3f}s")
            print(f"   • Slowest tool: {max(execution_times):.3f}s")
        
        print(f"\n🔧 Tool Categories:")
        categories = {}
        for result in self.test_results:
            tool_name = result["tool_name"]
            if "agent" in tool_name or "message" in tool_name:
                category = "Agent Management"
            elif "file" in tool_name or "read" in tool_name or "write" in tool_name:
                category = "File Operations"
            elif "chrome" in tool_name:
                category = "Chrome Integration"
            elif "service" in tool_name:
                category = "Service Management"
            elif "firebase" in tool_name:
                category = "Firebase"
            else:
                category = "System"
            
            if category not in categories:
                categories[category] = {"total": 0, "successful": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["successful"] += 1
        
        for category, stats in categories.items():
            success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"   • {category}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
        
        print("=" * 80)
        
        return successful_tests == total_tests


class MCPServerManager:
    """Manages MCP server for testing."""
    
    def __init__(self, server_script: str = "mcp_server.py"):
        self.server_script = Path(__file__).parent / server_script
        self.server_process: Optional[subprocess.Popen] = None
        
    async def start_server(self):
        """Start the MCP server."""
        logger.info("🚀 Starting MCP server for testing...")
        
        self.server_process = subprocess.Popen([
            sys.executable, str(self.server_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        await asyncio.sleep(3)
        
        # Check if server is running
        if self.server_process.poll() is None:
            logger.info("✅ MCP server started successfully")
            return True
        else:
            logger.error("❌ MCP server failed to start")
            return False
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.server_process:
            logger.info("🛑 Stopping MCP server...")
            self.server_process.terminate()
            try:
                await asyncio.wait_for(self.server_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.server_process.kill()
                await self.server_process.wait()
            logger.info("✅ MCP server stopped")


async def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server Integration Tests")
    parser.add_argument("--server-url", default="http://127.0.0.1:8001", help="MCP server URL (proxy recommended)")
    parser.add_argument("--start-server", action="store_true", help="Start server before testing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Start server if requested
    server_manager = None
    if args.start_server:
        server_manager = MCPServerManager()
        if not await server_manager.start_server():
            logger.error("❌ Failed to start server")
            return False
    
    try:
        # Run integration tests
        tester = MCPServerIntegrationTester(args.server_url)
        success = await tester.run_all_tests()
        
        # Print results
        tester.print_results()
        
        return success
        
    finally:
        # Stop server if we started it
        if server_manager:
            await server_manager.stop_server()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("⏸️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        sys.exit(1)