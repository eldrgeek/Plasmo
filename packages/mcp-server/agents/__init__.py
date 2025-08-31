"""
Agent management and communication modules for the MCP server.

This module provides functionality for managing multiple AI agents,
inter-agent communication, and coordination.
"""

from .agent_management import (
    get_agent_name, register_agent, set_custom_agent_name, get_custom_agent_name,
    get_agent_registration, list_registered_agents, update_agent_activity,
    is_agent_registered, unregister_agent, get_agent_stats
)
from .messaging import (
    create_message, get_messages, mark_message_read, delete_message,
    list_message_summaries, get_message_by_id, search_messages,
    get_message_thread, get_message_stats
)
from .notifications import (
    send_notification, get_pending_notifications, clear_notifications,
    set_cancel_flag, check_cancel_flag, clear_cancel_flag, get_notification_stats,
    wait_for_notifications
)
from .claude_instances import (
    launch_claude_instance, list_claude_instances, coordinate_claude_instances,
    send_inter_instance_message, get_instance_info, stop_instance, get_instance_stats,
    launch_claude_instance_tool, list_claude_instances_tool, 
    send_inter_instance_message_tool, coordinate_claude_instances_tool
)

__all__ = [
    # Agent management
    'get_agent_name',
    'register_agent',
    'set_custom_agent_name',
    'get_custom_agent_name',
    'get_agent_registration',
    'list_registered_agents',
    'update_agent_activity',
    'is_agent_registered',
    'unregister_agent',
    'get_agent_stats',
    
    # Messaging
    'create_message',
    'get_messages',
    'mark_message_read',
    'delete_message',
    'list_message_summaries',
    'get_message_by_id',
    'search_messages',
    'get_message_thread',
    'get_message_stats',
    
    # Notifications
    'send_notification',
    'get_pending_notifications',
    'clear_notifications',
    'set_cancel_flag',
    'check_cancel_flag',
    'clear_cancel_flag',
    'get_notification_stats',
    'wait_for_notifications',
    
    # Claude instances
    'launch_claude_instance',
    'list_claude_instances',
    'coordinate_claude_instances',
    'send_inter_instance_message',
    'get_instance_info',
    'stop_instance',
    'get_instance_stats',
    'launch_claude_instance_tool',
    'list_claude_instances_tool',
    'send_inter_instance_message_tool',
    'coordinate_claude_instances_tool'
]