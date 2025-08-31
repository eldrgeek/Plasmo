#!/usr/bin/env python3
"""
Claude Instances Module
========================

Provides Claude instance management functionality for the MCP server multi-agent system.

Features:
- Claude instance launching and management
- Inter-instance communication
- Instance coordination and task distribution
- Instance lifecycle management
- Integration with existing messaging system

"""

import os
import sys
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional

from .agent_management import get_agent_manager
from .messaging import get_message_manager

# Global instance manager
_instance_manager = None
_instance_lock = threading.Lock()


class ClaudeInstanceManager:
    """Manager for Claude Code instances and their coordination."""
    
    def __init__(self, messaging_root: Path = None):
        """Initialize Claude instance manager."""
        self.messaging_root = messaging_root or Path.cwd() / "messages"
        self.instances = {}  # instance_id -> instance_info
        self.instance_lock = threading.Lock()
        
        # Import the actual implementation if available
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            sys.path.insert(0, parent_dir)
            
            from claude_instance_launcher import ClaudeInstanceManager as ActualManager
            self.actual_manager = ActualManager()
            self.has_implementation = True
        except ImportError:
            self.actual_manager = None
            self.has_implementation = False
    
    def launch_claude_instance(self, role: str = "assistant", project_path: str = None, 
                             config_override: Dict[str, Any] = None, 
                             startup_message: str = None) -> Dict[str, Any]:
        """Launch a new Claude Code instance."""
        if not self.has_implementation:
            return {
                "success": False,
                "error": "Claude instance management implementation not available. Check claude_instance_launcher.py",
                "action": "launch_claude_instance"
            }
        
        try:
            result = self.actual_manager.launch_claude_instance(
                role, project_path, config_override, startup_message
            )
            
            if result.get("success"):
                # Store instance info locally
                with self.instance_lock:
                    self.instances[result["instance_id"]] = {
                        "id": result["instance_id"],
                        "role": role,
                        "project_path": project_path or os.getcwd(),
                        "status": "launched",
                        "created_at": result.get("timestamp"),
                        "config": result.get("config", {}),
                        "pid": result.get("pid")
                    }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during Claude instance launch: {str(e)}",
                "action": "launch_claude_instance"
            }
    
    def list_claude_instances(self) -> Dict[str, Any]:
        """List all active Claude instances."""
        if not self.has_implementation:
            return {
                "success": False,
                "error": "Claude instance management implementation not available",
                "action": "list_claude_instances"
            }
        
        try:
            result = self.actual_manager.list_instances()
            return {
                "success": True,
                "action": "list_claude_instances",
                "instances": result,
                "total_count": len(result),
                "active_count": len([i for i in result if i.get("status") == "launched"])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during instance listing: {str(e)}",
                "action": "list_claude_instances"
            }
    
    def send_inter_instance_message(self, target_instance_id: str, subject: str, 
                                   message: str, sender_role: str = "coordinator") -> Dict[str, Any]:
        """Send a message to another Claude instance."""
        if not self.has_implementation:
            return {
                "success": False,
                "error": "Claude instance management implementation not available",
                "action": "send_inter_instance_message"
            }
        
        try:
            result = self.actual_manager.send_message_to_instance(
                target_instance_id, sender_role, subject, message
            )
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during inter-instance message send: {str(e)}",
                "action": "send_inter_instance_message"
            }
    
    def coordinate_claude_instances(self, task: str, instance_ids: List[str] = None) -> Dict[str, Any]:
        """Coordinate multiple Claude instances for a task."""
        if not self.has_implementation:
            return {
                "success": False,
                "error": "Claude instance management implementation not available",
                "action": "coordinate_claude_instances"
            }
        
        try:
            result = self.actual_manager.coordinate_instances(task, instance_ids)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during instance coordination: {str(e)}",
                "action": "coordinate_claude_instances"
            }
    
    def get_instance_info(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific instance."""
        with self.instance_lock:
            return self.instances.get(instance_id)
    
    def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        """Stop a specific Claude instance."""
        if not self.has_implementation:
            return {
                "success": False,
                "error": "Claude instance management implementation not available",
                "action": "stop_instance"
            }
        
        try:
            # Try to stop via actual manager if available
            if hasattr(self.actual_manager, 'stop_instance'):
                result = self.actual_manager.stop_instance(instance_id)
            else:
                result = {"success": False, "error": "Stop functionality not implemented"}
            
            if result.get("success"):
                # Remove from local tracking
                with self.instance_lock:
                    if instance_id in self.instances:
                        self.instances[instance_id]["status"] = "stopped"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during instance stop: {str(e)}",
                "action": "stop_instance"
            }
    
    def get_instance_stats(self) -> Dict[str, Any]:
        """Get statistics about Claude instances."""
        with self.instance_lock:
            instances = list(self.instances.values())
        
        total_instances = len(instances)
        active_instances = len([i for i in instances if i.get("status") == "launched"])
        
        # Count by role
        role_counts = {}
        for instance in instances:
            role = instance.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_instances": total_instances,
            "active_instances": active_instances,
            "stopped_instances": total_instances - active_instances,
            "role_counts": role_counts,
            "has_implementation": self.has_implementation
        }


def get_claude_instance_manager(messaging_root: Path = None) -> ClaudeInstanceManager:
    """Get or create the global Claude instance manager."""
    global _instance_manager
    with _instance_lock:
        if _instance_manager is None:
            _instance_manager = ClaudeInstanceManager(messaging_root)
        return _instance_manager


# Convenience functions for direct use
def launch_claude_instance(role: str = "assistant", project_path: str = None, 
                          config_override: Dict[str, Any] = None, 
                          startup_message: str = None) -> Dict[str, Any]:
    """Launch a new Claude Code instance."""
    return get_claude_instance_manager().launch_claude_instance(
        role, project_path, config_override, startup_message
    )


def list_claude_instances() -> Dict[str, Any]:
    """List all active Claude instances."""
    return get_claude_instance_manager().list_claude_instances()


def send_inter_instance_message(target_instance_id: str, subject: str, 
                               message: str, sender_role: str = "coordinator") -> Dict[str, Any]:
    """Send a message to another Claude instance."""
    return get_claude_instance_manager().send_inter_instance_message(
        target_instance_id, subject, message, sender_role
    )


def coordinate_claude_instances(task: str, instance_ids: List[str] = None) -> Dict[str, Any]:
    """Coordinate multiple Claude instances for a task."""
    return get_claude_instance_manager().coordinate_claude_instances(task, instance_ids)


def get_instance_info(instance_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific instance."""
    return get_claude_instance_manager().get_instance_info(instance_id)


def stop_instance(instance_id: str) -> Dict[str, Any]:
    """Stop a specific Claude instance."""
    return get_claude_instance_manager().stop_instance(instance_id)


def get_instance_stats() -> Dict[str, Any]:
    """Get statistics about Claude instances."""
    return get_claude_instance_manager().get_instance_stats()


# Integration functions for backwards compatibility
def launch_claude_instance_tool(role: str = "assistant", project_path: str = None, 
                               startup_message: str = None) -> Dict[str, Any]:
    """Tool function for MCP server integration."""
    return launch_claude_instance(role, project_path, None, startup_message)


def list_claude_instances_tool() -> Dict[str, Any]:
    """Tool function for MCP server integration."""
    return list_claude_instances()


def send_inter_instance_message_tool(target_instance_id: str, subject: str, 
                                    message: str, sender_role: str = "coordinator") -> Dict[str, Any]:
    """Tool function for MCP server integration."""
    return send_inter_instance_message(target_instance_id, subject, message, sender_role)


def coordinate_claude_instances_tool(task: str, instance_ids: List[str] = None) -> Dict[str, Any]:
    """Tool function for MCP server integration."""
    return coordinate_claude_instances(task, instance_ids)