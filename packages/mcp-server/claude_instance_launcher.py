#!/usr/bin/env python3
"""
Claude Instance Launcher with Inter-Instance Communication
=========================================================

This tool extends the Plasmo MCP server to launch new Claude Code instances
and enable them to communicate with each other through the messaging system.

Key Features:
1. Launch new Claude Code instances in separate terminals
2. Automatic MCP server registration and agent naming
3. Inter-instance messaging through file-based communication
4. Shared project access with proper isolation
5. Coordination tools for multi-agent workflows
"""

import os
import sys
import json
import time
import uuid
import signal
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ClaudeInstanceManager:
    """Manages multiple Claude Code instances with inter-communication capabilities."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.instances = {}
        self.messaging_root = Path.home() / ".claude_instances"
        self.instances_file = self.messaging_root / "instances.json"
        self.setup_messaging_infrastructure()
    
    def setup_messaging_infrastructure(self):
        """Setup shared messaging infrastructure for all instances."""
        # Create messaging directories
        directories = [
            self.messaging_root,
            self.messaging_root / "instances",
            self.messaging_root / "messages", 
            self.messaging_root / "logs",
            self.messaging_root / "coordination"
        ]
        
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize instance registry
        if not self.instances_file.exists():
            self.instances_file.write_text("{}")
    
    def generate_instance_id(self) -> str:
        """Generate unique instance ID."""
        return f"claude_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def launch_claude_instance(
        self,
        role: str = "assistant",
        project_path: str = None,
        mcp_config: Dict = None,
        startup_message: str = None
    ) -> Dict[str, Any]:
        """
        Launch a new Claude Code instance with MCP server integration.
        
        Args:
            role: Role for this instance (e.g., "reviewer", "implementer", "coordinator")
            project_path: Path to project directory (defaults to current)
            mcp_config: Custom MCP server configuration
            startup_message: Initial message to send to the instance
        
        Returns:
            Dict with instance info and launch status
        """
        try:
            instance_id = self.generate_instance_id()
            project_path = project_path or str(self.project_root)
            
            # Create instance configuration
            instance_config = {
                "id": instance_id,
                "role": role,
                "project_path": project_path,
                "created_at": datetime.now().isoformat(),
                "status": "launching",
                "pid": None,
                "terminal_command": None
            }
            
            # Use existing MCP server (should always be running on port 8000)
            mcp_config = mcp_config or {
                "host": "localhost", 
                "port": 8000,  # Always use existing main server
                "agent_name": f"{role}_{instance_id}",
                "use_existing_server": True
            }
            
            # Create startup script that launches Claude with MCP server
            startup_script = self._create_startup_script(instance_id, instance_config, mcp_config)
            
            # Launch in new terminal window
            if sys.platform == "darwin":  # macOS
                terminal_cmd = [
                    "osascript", "-e",
                    f'''tell application "Terminal"
                        activate
                        do script "cd {project_path} && {startup_script}"
                    end tell'''
                ]
            elif sys.platform == "linux":
                terminal_cmd = [
                    "gnome-terminal", "--",
                    "bash", "-c", f"cd {project_path} && {startup_script}"
                ]
            else:  # Windows
                terminal_cmd = [
                    "cmd", "/c", "start", "cmd", "/k",
                    f"cd /d {project_path} && {startup_script}"
                ]
            
            # Execute launch command
            process = subprocess.Popen(terminal_cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            instance_config.update({
                "status": "launched",
                "pid": process.pid,
                "terminal_command": " ".join(terminal_cmd),
                "mcp_config": mcp_config
            })
            
            # Register instance
            self._register_instance(instance_id, instance_config)
            
            # Send startup message if provided
            if startup_message:
                time.sleep(3)  # Wait for instance to start
                self.send_message_to_instance(instance_id, "coordinator", 
                                            "Welcome", startup_message)
            
            return {
                "success": True,
                "instance_id": instance_id,
                "config": instance_config,
                "message": f"✅ Launched Claude instance '{role}' with ID: {instance_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to launch instance: {str(e)}"
            }
    
    def _create_startup_script(self, instance_id: str, instance_config: Dict, mcp_config: Dict) -> str:
        """Create startup script for Claude instance with MCP tools enabled."""
        
        script_content = f"""#!/bin/bash

# Set terminal color for visual distinction
printf '\e]11;#1a1a2e\a'  # Dark blue background
printf '\e]10;#ffffff\a'  # White text

echo "🚀 Starting Claude instance: {instance_id}"
echo "Role: {instance_config['role']}"
echo "Project: {instance_config['project_path']}"

# Set environment variables for this instance
export CLAUDE_INSTANCE_ID="{instance_id}"
export CLAUDE_ROLE="{instance_config['role']}"

echo "📋 Instance Configuration:"
echo "   • Instance ID: $CLAUDE_INSTANCE_ID"
echo "   • Role: $CLAUDE_ROLE" 
echo "   • Project: {instance_config['project_path']}"
echo ""

# Launch Claude CLI with MCP tools enabled (should be configured via .claude/settings.json)
echo "🚀 Starting Claude CLI..."
if command -v claude &> /dev/null; then
    echo "✅ Found Claude CLI"
    echo "🔧 MCP tools should be enabled via configuration"
    echo ""
    echo "📝 Suggested first command after Claude starts:"
    echo "   mcp__proxy__register_agent_with_name(agent_name='{mcp_config['agent_name']}')"
    echo ""
    claude
else
    echo "❌ 'claude' command not found"
    echo "ℹ️  Please install Claude CLI from: https://claude.ai/code"
    echo ""
    echo "Press any key to keep terminal open..."
    read -n 1
fi
"""
        
        script_path = self.messaging_root / f"startup_{instance_id}.sh"
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        return str(script_path)
    
    def _get_next_available_port(self) -> int:
        """Find next available port for MCP server."""
        import socket
        
        for port in range(8100, 8200):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return port
                except OSError:
                    continue
        
        raise RuntimeError("No available ports found")
    
    def _register_instance(self, instance_id: str, config: Dict):
        """Register instance in the global registry."""
        try:
            if self.instances_file.exists():
                with open(self.instances_file, 'r') as f:
                    instances = json.load(f)
            else:
                instances = {}
            
            instances[instance_id] = config
            
            with open(self.instances_file, 'w') as f:
                json.dump(instances, f, indent=2)
                
            self.instances[instance_id] = config
            
        except Exception as e:
            print(f"Warning: Could not register instance: {e}")
    
    def list_instances(self) -> List[Dict[str, Any]]:
        """List all registered Claude instances."""
        try:
            if self.instances_file.exists():
                with open(self.instances_file, 'r') as f:
                    instances = json.load(f)
                return list(instances.values())
            return []
        except Exception:
            return []
    
    def send_message_to_instance(self, target_instance_id: str, sender_role: str, 
                                subject: str, message: str) -> Dict[str, Any]:
        """Send message to specific Claude instance using Plasmo messaging system."""
        try:
            # Get target instance info
            instances = self.list_instances()
            target_instance = None
            
            for instance in instances:
                if instance["id"] == target_instance_id:
                    target_instance = instance
                    break
            
            if not target_instance:
                return {
                    "success": False,
                    "error": f"Target instance {target_instance_id} not found"
                }
            
            # Use Plasmo messaging system
            # This would integrate with the messages() function from mcp_server.py
            message_data = {
                "to": target_instance["mcp_config"]["agent_name"],
                "from": sender_role,
                "subject": subject,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "instance_id": target_instance_id
            }
            
            # Save message to shared messaging directory
            message_id = f"msg_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            message_file = self.messaging_root / "messages" / f"{message_id}.json"
            
            with open(message_file, 'w') as f:
                json.dump(message_data, f, indent=2)
            
            return {
                "success": True,
                "message_id": message_id,
                "target": target_instance_id,
                "message": "Message sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send message: {str(e)}"
            }
    
    def coordinate_instances(self, task: str, instances: List[str] = None) -> Dict[str, Any]:
        """Coordinate multiple instances for a collaborative task."""
        try:
            available_instances = self.list_instances()
            
            if not available_instances:
                return {
                    "success": False,
                    "error": "No instances available for coordination"
                }
            
            # Select instances for coordination
            if instances:
                selected_instances = [i for i in available_instances if i["id"] in instances]
            else:
                selected_instances = available_instances
            
            coordination_id = f"coord_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Send coordination message to all selected instances
            coordination_message = {
                "type": "coordination_request",
                "coordination_id": coordination_id,
                "task": task,
                "participants": [i["id"] for i in selected_instances],
                "coordinator": "system",
                "created_at": datetime.now().isoformat()
            }
            
            results = []
            for instance in selected_instances:
                result = self.send_message_to_instance(
                    instance["id"],
                    "coordinator",
                    f"Coordination Request: {coordination_id}",
                    json.dumps(coordination_message, indent=2)
                )
                results.append({
                    "instance_id": instance["id"],
                    "role": instance["role"],
                    "result": result
                })
            
            return {
                "success": True,
                "coordination_id": coordination_id,
                "task": task,
                "participants": len(selected_instances),
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Coordination failed: {str(e)}"
            }

# ============================================================================
# MCP TOOL INTEGRATION
# ============================================================================

def create_claude_instance_tools():
    """Create MCP tools for Claude instance management."""
    
    # Global instance manager
    instance_manager = ClaudeInstanceManager()
    
    def launch_claude_instance(
        role: str = "assistant",
        project_path: str = None,
        startup_message: str = None
    ) -> Dict[str, Any]:
        """
        Launch a new Claude Code instance with inter-communication capabilities.
        
        Args:
            role: Role for the instance (e.g., "reviewer", "implementer", "coordinator")
            project_path: Path to project directory (defaults to current)
            startup_message: Initial message to send to the new instance
        """
        return instance_manager.launch_claude_instance(role, project_path, None, startup_message)
    
    def list_claude_instances() -> Dict[str, Any]:
        """List all active Claude instances with their roles and status."""
        instances = instance_manager.list_instances()
        return {
            "success": True,
            "instances": instances,
            "total_count": len(instances)
        }
    
    def send_inter_instance_message(
        target_instance_id: str,
        subject: str,
        message: str,
        sender_role: str = "coordinator"
    ) -> Dict[str, Any]:
        """
        Send a message to another Claude instance.
        
        Args:
            target_instance_id: ID of the target Claude instance
            subject: Message subject
            message: Message content
            sender_role: Role of the sender (defaults to "coordinator")
        """
        return instance_manager.send_message_to_instance(
            target_instance_id, sender_role, subject, message
        )
    
    def coordinate_claude_instances(
        task: str,
        instance_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Coordinate multiple Claude instances for a collaborative task.
        
        Args:
            task: Description of the task to coordinate
            instance_ids: Specific instance IDs to coordinate (if None, uses all)
        """
        return instance_manager.coordinate_instances(task, instance_ids)
    
    return {
        "launch_claude_instance": launch_claude_instance,
        "list_claude_instances": list_claude_instances,
        "send_inter_instance_message": send_inter_instance_message,
        "coordinate_claude_instances": coordinate_claude_instances
    }

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for Claude instance management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Instance Manager")
    parser.add_argument("command", choices=["launch", "list", "send", "coordinate"])
    parser.add_argument("--role", default="assistant", help="Role for new instance")
    parser.add_argument("--project", help="Project path")
    parser.add_argument("--message", help="Startup or coordination message")
    parser.add_argument("--target", help="Target instance ID for messaging")
    parser.add_argument("--subject", help="Message subject")
    parser.add_argument("--instances", nargs="*", help="Instance IDs for coordination")
    
    args = parser.parse_args()
    
    manager = ClaudeInstanceManager()
    
    if args.command == "launch":
        result = manager.launch_claude_instance(args.role, args.project, None, args.message)
        print(json.dumps(result, indent=2))
    
    elif args.command == "list":
        instances = manager.list_instances()
        print(json.dumps({"instances": instances, "count": len(instances)}, indent=2))
    
    elif args.command == "send":
        if not args.target or not args.subject or not args.message:
            print("Error: send command requires --target, --subject, and --message")
            return
        
        result = manager.send_message_to_instance(args.target, "cli", args.subject, args.message)
        print(json.dumps(result, indent=2))
    
    elif args.command == "coordinate":
        if not args.message:
            print("Error: coordinate command requires --message (task description)")
            return
        
        result = manager.coordinate_instances(args.message, args.instances)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()