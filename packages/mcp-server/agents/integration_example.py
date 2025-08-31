#!/usr/bin/env python3
"""
Integration Example for Agent Management Modules

This example shows how to integrate the new modular agent management system
with the existing MCP server.
"""

# For MCP server integration, you would replace the existing agent functionality
# with imports from the new modules:

# Instead of the old agent_messaging.py AgentMessaging class, use:
from agents.agent_management import (
    get_agent_name, register_agent, set_custom_agent_name, get_custom_agent_name,
    get_agent_registration, list_registered_agents
)

from agents.messaging import (
    create_message, get_messages, mark_message_read, delete_message,
    list_message_summaries, get_message_by_id, search_messages
)

from agents.notifications import (
    send_notification, get_pending_notifications, clear_notifications,
    set_cancel_flag, check_cancel_flag, clear_cancel_flag
)

from agents.claude_instances import (
    launch_claude_instance_tool, list_claude_instances_tool,
    send_inter_instance_message_tool, coordinate_claude_instances_tool
)

# Example MCP tool integration:
def create_mcp_tools(mcp):
    """Create MCP tools using the new modular system."""
    
    @mcp.tool()
    def register_agent_with_name(agent_name: str):
        """Register current agent with a custom name."""
        try:
            set_custom_agent_name(agent_name)
            registration_info = register_agent()
            
            return {
                "success": True,
                "operation": "register_with_custom_name",
                "agent_name": agent_name,
                "registration": registration_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": "register_agent_with_name"
            }
    
    @mcp.tool()
    def get_current_agent_name():
        """Get the current agent name."""
        return {
            "success": True,
            "agent_name": get_agent_name(),
            "custom_name": get_custom_agent_name(),
            "is_custom": get_custom_agent_name() is not None
        }
    
    @mcp.tool()
    def messages(operation: str, payload: dict = None):
        """Multi-agent messaging system."""
        try:
            current_agent = get_agent_name()
            
            if operation == "send":
                if not payload or not all(k in payload for k in ["to", "subject", "message"]):
                    return {"success": False, "error": "Missing required fields"}
                
                message_data = create_message(
                    to=payload["to"],
                    subject=payload["subject"],
                    message=payload["message"],
                    reply_to=payload.get("reply_to")
                )
                
                return {
                    "success": True,
                    "operation": "send",
                    "message_id": message_data["id"],
                    "message": message_data
                }
            
            elif operation == "get":
                filters = payload or {}
                messages_list = get_messages(current_agent, filters)
                
                return {
                    "success": True,
                    "operation": "get",
                    "agent": current_agent,
                    "messages": messages_list
                }
            
            elif operation == "list":
                filters = payload or {}
                summaries = list_message_summaries(current_agent, filters)
                
                return {
                    "success": True,
                    "operation": "list",
                    "agent": current_agent,
                    "message_summaries": summaries,
                    "total_count": len(summaries)
                }
            
            elif operation == "agents":
                agents_list = list_registered_agents()
                return {
                    "success": True,
                    "operation": "agents",
                    "agents": agents_list,
                    "total_count": len(agents_list)
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }
    
    @mcp.tool()
    async def notify(operation: str, target_agent: str = None, message: str = None,
                    sender: str = None, agent_name: str = None):
        """Clean notification system."""
        try:
            current_agent = agent_name if agent_name else get_agent_name()
            
            if operation == "notify":
                if not target_agent or not message:
                    return {
                        "success": False,
                        "error": "notify operation requires 'target_agent' and 'message'"
                    }
                
                notification = send_notification(target_agent, message, sender)
                
                return {
                    "success": True,
                    "operation": "notify",
                    "notification_id": notification["id"],
                    "target_agent": target_agent,
                    "message": message
                }
            
            elif operation == "check":
                if not agent_name:
                    return {
                        "success": False,
                        "error": "check operation requires 'agent_name' parameter"
                    }
                
                notifications = get_pending_notifications(current_agent)
                
                return {
                    "success": True,
                    "operation": "check",
                    "notifications": notifications,
                    "count": len(notifications),
                    "agent_name": current_agent
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }
    
    # Claude instance management tools
    @mcp.tool()
    def launch_claude_instance(role: str = "assistant", project_path: str = None, 
                              startup_message: str = None):
        """Launch a new Claude Code instance."""
        return launch_claude_instance_tool(role, project_path, startup_message)
    
    @mcp.tool()
    def list_claude_instances():
        """List all active Claude instances."""
        return list_claude_instances_tool()
    
    @mcp.tool()
    def send_inter_instance_message(target_instance_id: str, subject: str, 
                                   message: str, sender_role: str = "coordinator"):
        """Send a message to another Claude instance."""
        return send_inter_instance_message_tool(target_instance_id, subject, message, sender_role)
    
    @mcp.tool()
    def coordinate_claude_instances(task: str, instance_ids: list = None):
        """Coordinate multiple Claude instances."""
        return coordinate_claude_instances_tool(task, instance_ids)

# Migration notes for the main MCP server:
MIGRATION_NOTES = """
MIGRATION STEPS FOR MCP_SERVER.PY:

1. Replace the existing agent_messaging.py import with:
   from agents.agent_management import get_agent_name, register_agent, set_custom_agent_name
   from agents.messaging import create_message, get_messages, mark_message_read, delete_message
   from agents.notifications import send_notification, get_pending_notifications
   from agents.claude_instances import launch_claude_instance_tool, list_claude_instances_tool

2. Remove the old AgentMessaging class instantiation and replace with direct function calls

3. Update the existing MCP tool functions to use the new module functions instead of 
   the old AgentMessaging class methods

4. The new modules are backward compatible and provide the same functionality with 
   better organization and maintainability

BENEFITS OF THE NEW MODULAR SYSTEM:
- Cleaner separation of concerns
- Better testability
- Easier maintenance
- More extensible architecture
- Reduced coupling between components
"""

print(MIGRATION_NOTES)