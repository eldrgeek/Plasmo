"""
Orchestration tools for multi-LLM coordination.

This module contains orchestration tools that were factored out from the main
MCP server to reduce complexity and provide specialized multi-LLM coordination functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.
"""

import sys
import os
import asyncio
import uuid
from typing import Dict, Any, List
from datetime import datetime

# Socket.IO import for orchestration
try:
    import socketio
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False

# Global Socket.IO client
socketio_client = None
socketio_connected = False


async def initialize_socketio_client():
    """Initialize Socket.IO client connection."""
    global socketio_client, socketio_connected
    
    if socketio_client is None:
        socketio_client = socketio.AsyncClient()
        
        @socketio_client.event
        async def connect():
            global socketio_connected
            socketio_connected = True
            print("✅ Connected to Socket.IO server for orchestration")
            
        @socketio_client.event
        async def disconnect():
            global socketio_connected
            socketio_connected = False
            print("❌ Disconnected from Socket.IO server")
            
        @socketio_client.event
        async def orchestration_response(data):
            print(f"📬 Received orchestration response: {data}")
    
    try:
        if not socketio_connected:
            await socketio_client.connect('http://localhost:3001')
        return True
    except Exception as e:
        print(f"Failed to connect to Socket.IO server: {e}")
        return False


def send_orchestration_command(
    command_type: str, 
    targets: List[str], 
    prompt: str, 
    options: Dict = None
) -> Dict[str, Any]:
    """
    Send orchestration command to extension via Socket.IO for multi-LLM coordination.
    
    This tool enables Claude Desktop to orchestrate multiple AI services (ChatGPT, Claude.ai, etc.)
    through the Chrome extension, collecting and aggregating their responses.
    
    Args:
        command_type: Type of command ('code_generation', 'analysis', 'chat')
        targets: List of AI services to target ['chatgpt', 'claude', 'perplexity']
        prompt: The prompt to send to all target AI services
        options: Optional parameters (timeout, priority, etc.)
        
    Returns:
        Dictionary with command dispatch status and tracking ID
        
    Example:
        send_orchestration_command(
            command_type="code_generation",
            targets=["chatgpt", "claude"],
            prompt="Build a React chat component",
            options={"timeout": 120}
        )
    """
    async def async_send_command():
        try:
            # Initialize Socket.IO client if needed
            connection_success = await initialize_socketio_client()
            if not connection_success:
                return {
                    "success": False, 
                    "error": "Failed to connect to Socket.IO server",
                    "details": "Ensure socketio_server.js is running on localhost:3001"
                }
            
            # Create orchestration command
            command_id = str(uuid.uuid4())
            command = {
                "id": command_id,
                "type": command_type,
                "prompt": prompt,
                "targets": targets,
                "timeout": options.get("timeout", 120) if options else 120,
                "priority": options.get("priority", "normal") if options else "normal",
                "timestamp": datetime.now().isoformat(),
                "source": "claude_desktop_mcp"
            }
            
            # Send command via Socket.IO
            await socketio_client.emit('orchestration_command', command)
            
            print(f"🚀 Sent orchestration command {command_id} to {len(targets)} targets")
            
            return {
                "success": True,
                "command_id": command_id,
                "targets": targets,
                "message": f"Orchestration command sent to {len(targets)} AI services",
                "tracking": {
                    "command_type": command_type,
                    "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "targets": targets,
                    "timeout": command.get("timeout"),
                    "timestamp": command.get("timestamp")
                }
            }
            
        except Exception as e:
            print(f"Error sending orchestration command: {e}")
            return {
                "success": False,
                "error": f"Failed to send orchestration command: {str(e)}",
                "error_type": type(e).__name__
            }
    
    # Run async function in event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_send_command())
            return result
        finally:
            loop.close()
    except Exception as e:
        return {
            "success": False,
            "error": f"Event loop error: {str(e)}",
            "details": "Failed to execute async Socket.IO operation"
        }
