"""
Claude instance management tools.

This module contains Claude instance management tools that were factored out from the main
MCP server to reduce complexity and provide specialized agent coordination functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.
"""

import sys
import os
from typing import Dict, Any, List

# Claude Instance Management Integration
current_dir = os.path.dirname(os.path.abspath(__file__))
try:
    from mcp_extension_claude_instances import (
        launch_claude_instance_tool,
        list_claude_instances_tool,
        send_inter_instance_message_tool,
        coordinate_claude_instances_tool
    )
    CLAUDE_INSTANCES_AVAILABLE = True
except ImportError as e:
    CLAUDE_INSTANCES_AVAILABLE = False


def launch_claude_instance(
    role: str = "assistant", 
    project_path: str = None, 
    startup_message: str = None
) -> Dict[str, Any]:
    """
    🚀 Launch a new Claude Code instance with inter-communication capabilities.
    
    Creates a new Claude instance in a separate terminal with its own MCP server,
    enabling multi-agent workflows and collaboration between Claude instances.
    
    Args:
        role: Role for the instance (e.g., "reviewer", "implementer", "coordinator", "tester")
        project_path: Path to project directory (defaults to current working directory)
        startup_message: Initial message to send to the new instance after launch
    
    Returns:
        Dict with launch status, instance ID, and configuration details
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return launch_claude_instance_tool(role, project_path, startup_message)


def list_claude_instances() -> Dict[str, Any]:
    """
    📋 List all active Claude instances with their roles and status.
    
    Shows all currently registered Claude instances, their roles, project paths,
    creation times, and communication endpoints.
    
    Returns:
        Dict with list of instances and summary statistics
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return list_claude_instances_tool()


def send_inter_instance_message(
    target_instance_id: str,
    subject: str, 
    message: str,
    sender_role: str = "coordinator"
) -> Dict[str, Any]:
    """
    💬 Send a message to another Claude instance for coordination.
    
    Enables communication between different Claude instances using the shared
    messaging system. Messages are delivered through the file-based messaging
    infrastructure.
    
    Args:
        target_instance_id: ID of the target Claude instance (from list_claude_instances)
        subject: Message subject line
        message: Message content (can include JSON data, instructions, etc.)
        sender_role: Role of the sender (defaults to "coordinator")
    
    Returns:
        Dict with message delivery status and message ID
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return send_inter_instance_message_tool(target_instance_id, subject, message, sender_role)


def coordinate_claude_instances(
    task: str,
    instance_ids: List[str] = None
) -> Dict[str, Any]:
    """
    🤝 Coordinate multiple Claude instances for a collaborative task.
    
    Sends coordination requests to multiple Claude instances simultaneously,
    enabling complex multi-agent workflows where different instances can
    work on different aspects of a larger task.
    
    Args:
        task: Description of the task to coordinate across instances
        instance_ids: Specific instance IDs to coordinate (if None, coordinates all instances)
    
    Returns:
        Dict with coordination results for each participating instance
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return coordinate_claude_instances_tool(task, instance_ids)