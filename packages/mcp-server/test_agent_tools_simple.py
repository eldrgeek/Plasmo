#!/usr/bin/env python3
"""
Simple Agent Tools Test using FastMCP Client
============================================

This test uses the FastMCP client library to test agent management tools
directly against the proxy server, avoiding HTTP session complexity.
"""

import asyncio
import sys
from pathlib import Path
from mcp.client.session import ClientSession
from mcp.client.streamable_http import StreamableHTTPTransport
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_agent_tools():
    """Test agent management tools using MCP client session."""
    base_url = "http://127.0.0.1:8001"
    
    try:
        # Create transport and session
        transport = StreamableHTTPTransport(base_url)
        session = ClientSession(transport)
        
        # Initialize session
        await session.initialize()
        logger.info("✅ Client session initialized")
        
        # List available tools
        tools_result = await session.list_tools()
        tools = tools_result.tools
        logger.info(f"📋 Found {len(tools)} tools")
        
        # Print first few tool names for debugging
        for i, tool in enumerate(tools[:5]):
            logger.info(f"   Tool {i+1}: {tool.name}")
        
        # Test register_agent_with_name
        result = await session.call_tool("register_agent_with_name", {
            "agent_name": "test_agent_simple"
        })
        logger.info(f"✅ register_agent_with_name: {result}")
        
        # Test get_current_agent_name
        result = await session.call_tool("get_current_agent_name", {})
        logger.info(f"✅ get_current_agent_name: {result}")
        
        # Test list_claude_instances
        result = await session.call_tool("list_claude_instances", {})
        logger.info(f"✅ list_claude_instances: {result}")
        
        logger.info("✅ All tests completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            await session.close()
        except:
            pass
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_agent_tools())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)