#!/usr/bin/env python3
"""
Agent Spawner - Utility for creating and managing Claude agent instances
Integrates with the existing MCP infrastructure to spawn specialized agents
"""

import json
import os
import subprocess
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class AgentConfig:
    """Configuration for spawning an agent"""
    agent_id: str
    role: str
    specialization: str
    template_file: str
    project_context: str
    initial_message: str
    mcp_server_path: str
    working_directory: str

class AgentSpawner:
    def __init__(self, project_root: str = "/Users/MikeWolf/Projects/Plasmo"):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / "agents"
        self.templates_dir = self.agents_dir / "agent_templates"
        self.active_agents_file = self.agents_dir / "active_agents.json"
        self.logs_dir = self.agents_dir / "logs"
        
        # Create necessary directories
        for dir_path in [self.agents_dir, self.templates_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize active agents registry
        if not self.active_agents_file.exists():
            self._save_active_agents([])
    
    def spawn_agent(self, role: str, specialization: str = "", 
                   project_context: str = "", target_project_dir: str = "", urgent: bool = False) -> Dict[str, Any]:
        """Spawn a new Claude agent instance"""
        
        # Generate unique agent ID
        agent_id = f"{role}_{specialization}_{int(time.time())}"
        
        # Find appropriate template
        template_file = self._find_template(role)
        if not template_file:
            return {"error": f"No template found for role: {role}"}
        
        # Determine working directory (default to Plasmo, but allow peer projects)
        working_dir = target_project_dir if target_project_dir else str(self.project_root)
        
        # Create agent configuration
        config = AgentConfig(
            agent_id=agent_id,
            role=role,
            specialization=specialization,
            template_file=str(template_file),
            project_context=project_context,
            initial_message=self._create_initial_message(role, specialization, project_context, working_dir),
            mcp_server_path=str(self.project_root / "packages/mcp-server/mcp_server.py"),
            working_directory=working_dir
        )
        
        # Spawn the Claude instance
        success = self._launch_claude_instance(config)
        
        if success:
            # Register agent
            self._register_agent(config)
            return {
                "success": True,
                "agent_id": agent_id,
                "role": role,
                "specialization": specialization,
                "message": f"Agent {agent_id} spawned successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to spawn agent {agent_id}"
            }
    
    def _find_template(self, role: str) -> Optional[Path]:
        """Find the appropriate template file for a role"""
        template_file = self.templates_dir / f"{role}.md"
        if template_file.exists():
            return template_file
        
        # Check for similar templates
        similar_templates = list(self.templates_dir.glob(f"*{role}*.md"))
        if similar_templates:
            return similar_templates[0]
        
        return None
    
    def _create_initial_message(self, role: str, specialization: str, context: str, working_dir: str) -> str:
        """Create the initial message for the agent"""
        template_path = self._find_template(role)
        
        initial_message = f"""You are being instantiated as a {role} agent with full Python execution capabilities.

Read your role definition and instructions from: {template_path}

Additional context:
- Specialization: {specialization}
- Project Context: {context}
- Working Directory: {working_dir}
- Agent System: {self.project_root}/agents/
- MCP Tools: Available via existing server on port 8000

IMPORTANT: You have access to all Python commands and can execute any Python code via the MCP server tools. Use these capabilities to accomplish your tasks efficiently.

Please confirm you understand your role and are ready to begin working."""
        
        return initial_message
    
    def _launch_claude_instance(self, config: AgentConfig) -> bool:
        """Launch a Claude instance with the given configuration in a visible terminal"""
        try:
            # Escape the initial message for AppleScript
            escaped_message = config.initial_message.replace('"', '\\"').replace('\n', '\\n')
            
            # Create the Claude command with MCP server connection and Python permissions
            claude_cmd = f'claude --server-url http://localhost:8000 "{escaped_message}"'
            
            # Set working directory
            env = os.environ.copy()
            env["CLAUDE_AGENT_ID"] = config.agent_id
            env["CLAUDE_AGENT_ROLE"] = config.role
            
            # Launch Claude in a new visible terminal window (macOS)
            # This creates a new Terminal window with a descriptive title
            terminal_script = f'''tell application "Terminal"
                activate
                set newTab to do script "cd {config.working_directory}"
                delay 1
                do script "echo '🤖 Launching {config.role} Agent'" in newTab
                do script "echo 'Working Directory: {config.working_directory}'" in newTab
                do script "echo 'Template: {config.template_file}'" in newTab
                do script "echo ''" in newTab
                do script "{claude_cmd}" in newTab
                set custom title of newTab to "Agent: {config.role}"
            end tell'''
            
            terminal_cmd = ["osascript", "-e", terminal_script]
            
            subprocess.Popen(terminal_cmd, env=env)
            
            # Log the launch
            self._log_agent_activity(config.agent_id, f"Launched Claude instance for {config.role} in visible terminal")
            
            return True
            
        except Exception as e:
            self._log_agent_activity(config.agent_id, f"Failed to launch: {str(e)}")
            return False
    
    def _register_agent(self, config: AgentConfig):
        """Register the agent in the active agents registry"""
        active_agents = self._load_active_agents()
        
        agent_record = {
            "agent_id": config.agent_id,
            "role": config.role,
            "specialization": config.specialization,
            "status": "active",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_activity": time.strftime("%Y-%m-%d %H:%M:%S"),
            "template_file": config.template_file,
            "project_context": config.project_context,
            "current_tasks": [],
            "performance_score": 1.0
        }
        
        active_agents.append(agent_record)
        self._save_active_agents(active_agents)
    
    def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all currently active agents"""
        return self._load_active_agents()
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        active_agents = self._load_active_agents()
        for agent in active_agents:
            if agent["agent_id"] == agent_id:
                return agent
        return None
    
    def retire_agent(self, agent_id: str) -> bool:
        """Retire an agent (mark as inactive)"""
        active_agents = self._load_active_agents()
        
        for i, agent in enumerate(active_agents):
            if agent["agent_id"] == agent_id:
                agent["status"] = "retired"
                agent["retired_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._save_active_agents(active_agents)
                self._log_agent_activity(agent_id, "Agent retired")
                return True
        
        return False
    
    def _load_active_agents(self) -> List[Dict[str, Any]]:
        """Load active agents from registry"""
        if not self.active_agents_file.exists():
            return []
        
        try:
            with open(self.active_agents_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_active_agents(self, agents: List[Dict[str, Any]]):
        """Save active agents to registry"""
        with open(self.active_agents_file, 'w') as f:
            json.dump(agents, f, indent=2)
    
    def _log_agent_activity(self, agent_id: str, message: str):
        """Log agent activity"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {agent_id}: {message}\n"
        
        log_file = self.logs_dir / "agent_spawner.log"
        with open(log_file, 'a') as f:
            f.write(log_entry)

# CLI Interface
def main():
    spawner = AgentSpawner()
    
    print("🤖 Agent Spawner - Claude Agent Management")
    print("Commands: spawn, list, status, retire, quit")
    
    while True:
        command = input("\nSpawner> ").strip().lower()
        
        if command == "quit":
            break
        elif command == "spawn":
            role = input("Agent role: ").strip()
            specialization = input("Specialization (optional): ").strip()
            context = input("Project context (optional): ").strip()
            target_dir = input("Target project directory (optional, default: Plasmo): ").strip()
            
            result = spawner.spawn_agent(role, specialization, context, target_dir)
            if result.get("success"):
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['error']}")
        
        elif command == "list":
            agents = spawner.list_active_agents()
            if agents:
                print("\n📋 Active Agents:")
                for agent in agents:
                    print(f"  {agent['agent_id']}: {agent['role']} ({agent['status']})")
            else:
                print("No active agents")
        
        elif command == "status":
            agent_id = input("Agent ID: ").strip()
            status = spawner.get_agent_status(agent_id)
            if status:
                print(json.dumps(status, indent=2))
            else:
                print(f"Agent {agent_id} not found")
        
        elif command == "retire":
            agent_id = input("Agent ID: ").strip()
            if spawner.retire_agent(agent_id):
                print(f"✅ Agent {agent_id} retired")
            else:
                print(f"❌ Agent {agent_id} not found")
        
        else:
            print("Unknown command. Available: spawn, list, status, retire, quit")

if __name__ == "__main__":
    main()