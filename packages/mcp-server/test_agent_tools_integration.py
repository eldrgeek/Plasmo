#!/usr/bin/env python3
"""
Agent Management Tools Integration Tests
========================================

This module tests all 8 agent management tools against the running MCP server.
Tests include real agent registration, messaging, notifications, and Claude instances.

Usage:
    python test_agent_tools_integration.py
    python test_agent_tools_integration.py --server-url http://127.0.0.1:8000
"""

import asyncio
import aiohttp
import json
import sys
import time
import tempfile
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_sse_response(text: str) -> Dict[str, Any]:
    """Parse Server-Sent Events response format.
    
    Expected format:
    event: message
    data: {"jsonrpc":"2.0","id":1,"result":{...}}
    """
    try:
        lines = text.strip().split('\n')
        data_line = None
        
        for line in lines:
            if line.startswith('data: '):
                data_line = line[6:]  # Remove 'data: ' prefix
                break
        
        if data_line:
            return json.loads(data_line)
        else:
            return {"error": "No data line found in SSE response", "raw_text": text}
            
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {e}", "raw_text": text}
    except Exception as e:
        return {"error": f"SSE parse error: {e}", "raw_text": text}

class AgentToolsIntegrationTester:
    """Integration tester for agent management tools."""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8001"):
        self.server_url = server_url
        self.mcp_endpoint = f"{server_url}/mcp/"
        self.health_endpoint = f"{server_url}/health"
        self.session = None
        self.test_results = []
        self.session_id = None
        
        # Test data
        self.test_agent_name = f"test_agent_{uuid.uuid4().hex[:8]}"
        self.test_message_id = None
        self.test_notification_id = None
        
    async def start_session(self):
        """Start HTTP session for testing."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        self.session = aiohttp.ClientSession(headers=headers)
        
        # Initialize MCP session
        await self.initialize_mcp_session()
        
    async def stop_session(self):
        """Stop HTTP session."""
        if self.session:
            await self.session.close()
    
    async def initialize_mcp_session(self):
        """Initialize MCP session with proper protocol."""
        try:
            # Initialize session
            init_request = {
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
                        "name": "agent-tools-integration-tester",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with self.session.post(self.mcp_endpoint, json=init_request) as response:
                if response.status == 200:
                    text = await response.text()
                    result = parse_sse_response(text)
                    
                    if "error" in result:
                        logger.error(f"❌ MCP initialization failed: {result['error']}")
                        return False
                    
                    logger.info("✅ MCP session initialized")
                    return True
                else:
                    logger.error(f"❌ MCP initialization failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ MCP session initialization error: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific MCP tool."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                }
            }
            
            async with self.session.post(self.mcp_endpoint, json=request) as response:
                if response.status == 200:
                    text = await response.text()
                    result = parse_sse_response(text)
                    
                    if "error" in result:
                        return {"error": result["error"], "details": result.get("raw_text", "")}
                    
                    return result.get("result", {})
                else:
                    error_text = await response.text()
                    return {"error": f"HTTP {response.status}", "details": error_text}
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def test_tool(self, tool_name: str, arguments: Dict[str, Any] = None, 
                       expected_keys: List[str] = None, description: str = None) -> Dict[str, Any]:
        """Test a specific tool and validate response."""
        logger.info(f"🧪 Testing {tool_name}: {description or 'No description'}")
        
        start_time = time.time()
        result = await self.call_tool(tool_name, arguments)
        end_time = time.time()
        
        test_result = {
            "tool_name": tool_name,
            "description": description,
            "execution_time": round(end_time - start_time, 3),
            "success": "error" not in result,
            "result": result,
            "arguments": arguments
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
        
        if not test_result["success"]:
            logger.error(f"   Error: {result.get('error', 'Unknown error')}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def test_register_agent_with_name(self):
        """Test agent registration with custom name."""
        result = await self.test_tool(
            "register_agent_with_name",
            {"agent_name": self.test_agent_name},
            ["success", "agent_name"],
            "Register agent with custom name"
        )
        
        # Verify the agent was actually registered
        if result["success"]:
            returned_name = result["result"].get("agent_name")
            if returned_name != self.test_agent_name:
                logger.error(f"   Expected agent name {self.test_agent_name}, got {returned_name}")
        
        return result
    
    async def test_get_current_agent_name(self):
        """Test getting current agent name."""
        result = await self.test_tool(
            "get_current_agent_name",
            {},
            ["agent_name"],
            "Get current agent name"
        )
        
        # Verify the agent name matches what we set
        if result["success"]:
            current_name = result["result"].get("agent_name")
            if current_name != self.test_agent_name:
                logger.warning(f"   Current agent name {current_name} != registered name {self.test_agent_name}")
        
        return result
    
    async def test_messages_send(self):
        """Test sending a message."""
        target_agent = f"target_{uuid.uuid4().hex[:8]}"
        
        result = await self.test_tool(
            "messages",
            {
                "operation": "send",
                "payload": {
                    "to": target_agent,
                    "subject": "Test Message",
                    "message": "Hello from integration test",
                    "reply_to": None
                }
            },
            ["success", "message_id"],
            "Send message to another agent"
        )
        
        # Store message ID for later tests
        if result["success"]:
            self.test_message_id = result["result"].get("message_id")
        
        return result
    
    async def test_messages_get(self):
        """Test getting messages."""
        result = await self.test_tool(
            "messages",
            {
                "operation": "get",
                "payload": {}
            },
            ["messages"],
            "Get messages for current agent"
        )
        
        # Verify we can see the message we sent
        if result["success"]:
            messages = result["result"].get("messages", [])
            logger.info(f"   Retrieved {len(messages)} messages")
            
            # Look for our test message
            found_message = False
            for msg in messages:
                if msg.get("id") == self.test_message_id:
                    found_message = True
                    logger.info(f"   Found our test message: {msg.get('subject')}")
                    break
            
            if not found_message and self.test_message_id:
                logger.warning(f"   Test message {self.test_message_id} not found in results")
        
        return result
    
    async def test_messages_list(self):
        """Test listing message summaries."""
        result = await self.test_tool(
            "messages",
            {
                "operation": "list",
                "payload": {}
            },
            ["messages"],
            "List message summaries"
        )
        
        if result["success"]:
            messages = result["result"].get("messages", [])
            logger.info(f"   Listed {len(messages)} message summaries")
        
        return result
    
    async def test_notify_send(self):
        """Test sending a notification."""
        target_agent = f"notify_target_{uuid.uuid4().hex[:8]}"
        
        result = await self.test_tool(
            "notify",
            {
                "operation": "notify",
                "target_agent": target_agent,
                "message": "Test notification from integration test",
                "sender": self.test_agent_name
            },
            ["success"],
            "Send notification to another agent"
        )
        
        if result["success"]:
            self.test_notification_id = result["result"].get("notification_id")
        
        return result
    
    async def test_notify_check(self):
        """Test checking for notifications."""
        result = await self.test_tool(
            "notify",
            {
                "operation": "check",
                "agent_name": self.test_agent_name
            },
            ["notifications"],
            "Check for pending notifications"
        )
        
        if result["success"]:
            notifications = result["result"].get("notifications", [])
            logger.info(f"   Found {len(notifications)} pending notifications")
        
        return result
    
    async def test_launch_claude_instance(self):
        """Test launching a Claude instance."""
        result = await self.test_tool(
            "launch_claude_instance",
            {
                "role": "test_reviewer",
                "project_path": str(Path(__file__).parent),
                "startup_message": "Integration test instance"
            },
            ["success"],
            "Launch new Claude instance"
        )
        
        if result["success"]:
            instance_id = result["result"].get("instance_id")
            logger.info(f"   Launched instance: {instance_id}")
        
        return result
    
    async def test_list_claude_instances(self):
        """Test listing Claude instances."""
        result = await self.test_tool(
            "list_claude_instances",
            {},
            ["instances"],
            "List active Claude instances"
        )
        
        if result["success"]:
            instances = result["result"].get("instances", [])
            logger.info(f"   Found {len(instances)} active instances")
            
            for instance in instances:
                logger.info(f"   Instance: {instance.get('instance_id')} - {instance.get('role')}")
        
        return result
    
    async def test_send_inter_instance_message(self):
        """Test sending message between instances."""
        # First, list instances to find a target
        instances_result = await self.call_tool("list_claude_instances")
        
        if "error" in instances_result:
            logger.warning("   Cannot test inter-instance messaging - no instances available")
            return {
                "tool_name": "send_inter_instance_message",
                "success": False,
                "error": "No instances available for testing",
                "execution_time": 0
            }
        
        instances = instances_result.get("instances", [])
        if not instances:
            logger.warning("   No instances available for inter-instance messaging test")
            return {
                "tool_name": "send_inter_instance_message", 
                "success": False,
                "error": "No instances available",
                "execution_time": 0
            }
        
        target_instance = instances[0]["instance_id"]
        
        result = await self.test_tool(
            "send_inter_instance_message",
            {
                "target_instance_id": target_instance,
                "subject": "Test Inter-Instance Message",
                "message": "Hello from integration test",
                "sender_role": "test_sender"
            },
            ["success"],
            "Send message between Claude instances"
        )
        
        return result
    
    async def test_coordinate_claude_instances(self):
        """Test coordinating multiple Claude instances."""
        result = await self.test_tool(
            "coordinate_claude_instances",
            {
                "task": "Integration test coordination task",
                "instance_ids": None  # Coordinate all instances
            },
            ["success"],
            "Coordinate multiple Claude instances"
        )
        
        if result["success"]:
            coordination_results = result["result"].get("coordination_results", {})
            logger.info(f"   Coordinated {len(coordination_results)} instances")
        
        return result
    
    async def run_all_tests(self):
        """Run all agent management tool tests."""
        logger.info("🚀 Starting Agent Management Tools Integration Tests")
        logger.info("=" * 60)
        
        await self.start_session()
        
        try:
            # Test agent registration and naming
            await self.test_register_agent_with_name()
            await self.test_get_current_agent_name()
            
            # Test messaging functionality
            await self.test_messages_send()
            await self.test_messages_get()
            await self.test_messages_list()
            
            # Test notification system
            await self.test_notify_send()
            await self.test_notify_check()
            
            # Test Claude instance management
            await self.test_launch_claude_instance()
            await self.test_list_claude_instances()
            await self.test_send_inter_instance_message()
            await self.test_coordinate_claude_instances()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
        finally:
            await self.stop_session()
    
    def print_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 80)
        print("🎯 Agent Management Tools Integration Test Results")
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
        execution_times = [r["execution_time"] for r in self.test_results]
        if execution_times:
            print(f"   • Average execution time: {sum(execution_times) / len(execution_times):.3f}s")
            print(f"   • Fastest tool: {min(execution_times):.3f}s")
            print(f"   • Slowest tool: {max(execution_times):.3f}s")
        
        print(f"\n🔧 Detailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} {result['tool_name']} - {result['execution_time']}s")
            if result.get("description"):
                print(f"        {result['description']}")
        
        print("=" * 80)
        
        return successful_tests == total_tests


async def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Management Tools Integration Tests")
    parser.add_argument("--server-url", default="http://127.0.0.1:8001", help="MCP server URL (proxy recommended)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create tester
    tester = AgentToolsIntegrationTester(args.server_url)
    
    try:
        # Run tests
        success = await tester.run_all_tests()
        
        # Print results
        tester.print_results()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("⏸️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)