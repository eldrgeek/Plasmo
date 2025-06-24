#!/usr/bin/env python3
"""
MCP Extension: Claude Instance Management
========================================

This extends the Plasmo MCP server with Claude instance management capabilities.
Add these tools to mcp_server.py to enable multi-Claude coordination.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from claude_instance_launcher import ClaudeInstanceManager
from typing import Dict, List, Any

# Global instance manager
_instance_manager = None

def get_instance_manager():
    """Get or create the global instance manager."""
    global _instance_manager
    if _instance_manager is None:
        _instance_manager = ClaudeInstanceManager()
    return _instance_manager

# ============================================================================
# MCP TOOLS FOR PLASMO SERVER
# ============================================================================

def launch_claude_instance_tool(
    role: str = "assistant",
    project_path: str = None,
    startup_message: str = None
) -> Dict[str, Any]:
    """
    🚀 Launch a new Claude Code instance with inter-communication capabilities.
    
    This tool creates a new Claude instance in a separate terminal with its own
    MCP server, enabling multi-agent workflows and collaboration.
    
    Args:
        role: Role for the instance (e.g., "reviewer", "implementer", "coordinator", "tester")
        project_path: Path to project directory (defaults to current working directory)
        startup_message: Initial message to send to the new instance after launch
    
    Returns:
        Dict with launch status, instance ID, and configuration details
    
    Example:
        # Launch a code reviewer instance
        launch_claude_instance_tool("reviewer", "/path/to/project", "Please review the latest changes")
        
        # Launch a testing specialist
        launch_claude_instance_tool("tester", startup_message="Focus on testing the new features")
    """
    try:
        manager = get_instance_manager()
        result = manager.launch_claude_instance(role, project_path, None, startup_message)
        
        if result.get("success"):
            return {
                "success": True,
                "action": "launch_claude_instance",
                "instance_id": result["instance_id"],
                "role": role,
                "project_path": project_path or os.getcwd(),
                "message": result["message"],
                "config": result["config"]
            }
        else:
            return {
                "success": False,
                "action": "launch_claude_instance",
                "error": result.get("error", "Unknown error occurred")
            }
            
    except Exception as e:
        return {
            "success": False,
            "action": "launch_claude_instance",
            "error": f"Exception during launch: {str(e)}"
        }

def list_claude_instances_tool() -> Dict[str, Any]:
    """
    📋 List all active Claude instances with their roles and status.
    
    Shows all currently registered Claude instances, their roles, project paths,
    creation times, and communication endpoints.
    
    Returns:
        Dict with list of instances and summary statistics
    
    Example Response:
        {
            "instances": [
                {
                    "id": "claude_1234567890_abcd1234",
                    "role": "reviewer",
                    "status": "launched",
                    "project_path": "/path/to/project",
                    "created_at": "2024-01-01T12:00:00"
                }
            ],
            "total_count": 1
        }
    """
    try:
        manager = get_instance_manager()
        instances = manager.list_instances()
        
        # Add status information
        active_instances = []
        for instance in instances:
            instance_info = {
                "id": instance["id"],
                "role": instance["role"],
                "status": instance["status"],
                "project_path": instance["project_path"],
                "created_at": instance["created_at"],
                "pid": instance.get("pid"),
                "mcp_port": instance.get("mcp_config", {}).get("port")
            }
            active_instances.append(instance_info)
        
        return {
            "success": True,
            "action": "list_claude_instances",
            "instances": active_instances,
            "total_count": len(active_instances),
            "active_count": len([i for i in active_instances if i["status"] == "launched"])
        }
        
    except Exception as e:
        return {
            "success": False,
            "action": "list_claude_instances",
            "error": f"Failed to list instances: {str(e)}"
        }

def send_inter_instance_message_tool(
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
    
    Example:
        # Send a task to a reviewer instance
        send_inter_instance_message_tool(
            "claude_1234567890_abcd1234",
            "Code Review Request", 
            "Please review the changes in /src/components/NewFeature.jsx",
            "implementer"
        )
    """
    try:
        if not target_instance_id or not subject or not message:
            return {
                "success": False,
                "action": "send_inter_instance_message",
                "error": "Missing required parameters: target_instance_id, subject, and message are required"
            }
        
        manager = get_instance_manager()
        result = manager.send_message_to_instance(target_instance_id, sender_role, subject, message)
        
        if result.get("success"):
            return {
                "success": True,
                "action": "send_inter_instance_message",
                "message_id": result["message_id"],
                "target_instance": target_instance_id,
                "subject": subject,
                "sender_role": sender_role,
                "message": "Message sent successfully"
            }
        else:
            return {
                "success": False,
                "action": "send_inter_instance_message",
                "error": result.get("error", "Failed to send message")
            }
            
    except Exception as e:
        return {
            "success": False,
            "action": "send_inter_instance_message",
            "error": f"Exception during message send: {str(e)}"
        }

def coordinate_claude_instances_tool(
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
    
    Example:
        # Coordinate code review across multiple instances
        coordinate_claude_instances_tool(
            "Review and test the new authentication system",
            ["claude_reviewer_123", "claude_tester_456"]
        )
        
        # Coordinate all instances for a complex task
        coordinate_claude_instances_tool(
            "Implement new feature: user dashboard with real-time updates"
        )
    """
    try:
        if not task:
            return {
                "success": False,
                "action": "coordinate_claude_instances",
                "error": "Task description is required"
            }
        
        manager = get_instance_manager()
        result = manager.coordinate_instances(task, instance_ids)
        
        if result.get("success"):
            return {
                "success": True,
                "action": "coordinate_claude_instances",
                "coordination_id": result["coordination_id"],
                "task": task,
                "participants": result["participants"],
                "results": result["results"],
                "message": f"Coordination request sent to {result['participants']} instances"
            }
        else:
            return {
                "success": False,
                "action": "coordinate_claude_instances",
                "error": result.get("error", "Coordination failed")
            }
            
    except Exception as e:
        return {
            "success": False,
            "action": "coordinate_claude_instances",
            "error": f"Exception during coordination: {str(e)}"
        }

def get_instance_messages_tool(
    agent_name: str = None,
    filters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    📨 Get messages for the current or specified Claude instance.
    
    Retrieves messages from the shared messaging system for inter-instance
    communication. Can filter by sender, subject, read status, etc.
    
    Args:
        agent_name: Agent name to get messages for (defaults to current instance)
        filters: Optional filters (e.g., {"read": False, "from": "coordinator"})
    
    Returns:
        Dict with messages and summary information
    """
    try:
        # This would integrate with the existing messages() function from Plasmo
        # For now, return a placeholder that shows the integration point
        return {
            "success": True,
            "action": "get_instance_messages",
            "integration_note": "This tool integrates with the existing messages() function in Plasmo MCP server",
            "usage": "Use the existing 'messages' tool with operation='get' for full functionality"
        }
        
    except Exception as e:
        return {
            "success": False,
            "action": "get_instance_messages",
            "error": f"Failed to retrieve messages: {str(e)}"
        }

# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

INTEGRATION_INSTRUCTIONS = """
To integrate these Claude instance management tools into the Plasmo MCP server:

1. ADD IMPORTS to mcp_server.py:
   ```python
   from mcp_extension_claude_instances import (
       launch_claude_instance_tool,
       list_claude_instances_tool, 
       send_inter_instance_message_tool,
       coordinate_claude_instances_tool
   )
   ```

2. ADD MCP TOOL DECORATORS:
   ```python
   @mcp.tool()
   def launch_claude_instance(role: str = "assistant", project_path: str = None, startup_message: str = None):
       return launch_claude_instance_tool(role, project_path, startup_message)
   
   @mcp.tool()  
   def list_claude_instances():
       return list_claude_instances_tool()
   
   @mcp.tool()
   def send_inter_instance_message(target_instance_id: str, subject: str, message: str, sender_role: str = "coordinator"):
       return send_inter_instance_message_tool(target_instance_id, subject, message, sender_role)
   
   @mcp.tool()
   def coordinate_claude_instances(task: str, instance_ids: List[str] = None):
       return coordinate_claude_instances_tool(task, instance_ids)
   ```

3. UPDATE TOOL COUNT in server info (add 4 new tools)

4. RESTART MCP SERVER to activate new tools

USAGE EXAMPLES:

1. Launch a specialized instance:
   launch_claude_instance("code_reviewer", "/path/to/project", "Focus on security and performance")

2. Send coordination messages:
   send_inter_instance_message("claude_reviewer_123", "Review Request", "Please review PR #42")

3. Coordinate complex tasks:
   coordinate_claude_instances("Implement OAuth2 authentication system")

4. List and monitor instances:
   list_claude_instances()
"""

if __name__ == "__main__":
    print("Claude Instance Management MCP Extension")
    print("=" * 50)
    print(INTEGRATION_INSTRUCTIONS)