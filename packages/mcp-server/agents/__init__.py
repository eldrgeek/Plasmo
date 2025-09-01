"""
Agent management tools module.

This module contains Claude instance management tools that were factored out from the main
MCP server to reduce complexity and provide specialized agent coordination functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.
"""

from .claude_instances import (
    launch_claude_instance,
    list_claude_instances,
    send_inter_instance_message,
    coordinate_claude_instances
)

__all__ = [
    'launch_claude_instance',
    'list_claude_instances', 
    'send_inter_instance_message',
    'coordinate_claude_instances'
]