#!/usr/bin/env python3
"""
Agent Tools Test using STDIO MCP Client
=======================================

This test uses STDIO transport to test agent management tools directly,
bypassing the HTTP session complexity.
"""

import asyncio
import subprocess
import json
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class STDIOTester:
    """Test MCP tools using STDIO transport."""
    
    def __init__(self):
        self.process = None
        self.request_id = 1
        
    async def start_server(self):
        """Start MCP server in STDIO mode."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, "mcp_server.py", "--stdio",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            logger.info("✅ MCP server started in STDIO mode")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            return False
    
    async def send_request(self, method: str, params: dict = None):
        """Send JSON-RPC request to server."""
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        self.request_id += 1
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        return response
    
    async def initialize(self):
        """Initialize MCP session."""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "stdio-tester",
                "version": "1.0.0"
            }
        })
        
        if "result" in response:
            logger.info("✅ MCP session initialized")
            return True
        else:
            logger.error(f"❌ Failed to initialize: {response}")
            return False
    
    async def list_tools(self):
        """List available tools."""
        response = await self.send_request("tools/list")
        
        if "result" in response:
            tools = response["result"]["tools"]
            logger.info(f"📋 Found {len(tools)} tools")
            return tools
        else:
            logger.error(f"❌ Failed to list tools: {response}")
            return []
    
    async def call_tool(self, name: str, arguments: dict = None):
        """Call a specific tool."""
        response = await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        
        if "result" in response:
            logger.info(f"✅ {name}: {response['result']}")
            return response["result"]
        else:
            logger.error(f"❌ {name} failed: {response}")
            return {"error": response.get("error", "Unknown error")}
    
    async def stop_server(self):
        """Stop the server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("🛑 Server stopped")
    
    async def test_agent_tools(self):
        """Test agent management tools."""
        logger.info("🚀 Starting Agent Tools STDIO Test")
        
        if not await self.start_server():
            return False
        
        try:
            # Initialize session
            if not await self.initialize():
                return False
            
            # List tools
            tools = await self.list_tools()
            if not tools:
                return False
            
            # Print tool names
            logger.info("Available tools:")
            for tool in tools[:10]:  # Show first 10
                logger.info(f"   - {tool['name']}")
            
            # Test register_agent_with_name
            result = await self.call_tool("register_agent_with_name", {
                "agent_name": "test_stdio_agent"
            })
            
            # Test get_current_agent_name
            result = await self.call_tool("get_current_agent_name")
            
            # Test list_claude_instances
            result = await self.call_tool("list_claude_instances")
            
            # Test messages operation
            result = await self.call_tool("messages", {
                "operation": "register"
            })
            
            logger.info("✅ All agent tools tests completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False
        finally:
            await self.stop_server()

async def main():
    """Main test runner."""
    tester = STDIOTester()
    success = await tester.test_agent_tools()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("⏸️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)