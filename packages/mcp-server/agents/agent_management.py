#!/usr/bin/env python3
"""
Agent Management Module
======================

Provides core agent management functionality including registration,
naming, and agent discovery for the MCP server multi-agent system.

Features:
- Agent registration and discovery
- Custom agent naming with directory fallback
- Agent information storage and retrieval
- Thread-safe operations

"""

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class AgentManager:
    """Core agent management functionality for the MCP server."""
    
    def __init__(self, messaging_root: Path = None):
        """Initialize agent manager with optional custom root directory."""
        self.messaging_root = messaging_root or Path.cwd() / "messages"
        self.custom_agent_name = None
        self.registration_lock = threading.Lock()
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.messaging_root,
            self.get_agents_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_agents_dir(self) -> Path:
        """Get agents directory."""
        return self.messaging_root / "agents"
    
    def set_custom_agent_name(self, name: str):
        """Set custom agent name."""
        self.custom_agent_name = name
    
    def get_custom_agent_name(self) -> Optional[str]:
        """Get custom agent name if set."""
        return self.custom_agent_name
    
    def get_agent_name(self) -> str:
        """Get agent name - custom name if set, otherwise current directory name."""
        if self.custom_agent_name:
            return self.custom_agent_name
        return Path.cwd().name
    
    def register_agent(self) -> Dict[str, Any]:
        """Register current agent in the messaging system."""
        with self.registration_lock:
            agent_name = self.get_agent_name()
            agent_dir = self.get_agents_dir() / agent_name
            agent_dir.mkdir(exist_ok=True)
            
            registration_data = {
                "name": agent_name,
                "registered_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "pid": os.getpid(),
                "working_directory": str(Path.cwd()),
                "custom_name": self.custom_agent_name is not None
            }
            
            registration_file = agent_dir / "registration.json"
            with open(registration_file, 'w', encoding='utf-8') as f:
                json.dump(registration_data, f, indent=2)
            
            return registration_data
    
    def get_agent_registration(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent registration information."""
        agent_dir = self.get_agents_dir() / agent_name
        registration_file = agent_dir / "registration.json"
        
        if not registration_file.exists():
            return None
        
        try:
            with open(registration_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def list_registered_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        agents = []
        
        for agent_dir in self.get_agents_dir().iterdir():
            if agent_dir.is_dir():
                agent_info = self.get_agent_registration(agent_dir.name)
                if agent_info:
                    agents.append(agent_info)
        
        return agents
    
    def update_agent_activity(self, agent_name: str = None) -> bool:
        """Update agent's last activity timestamp."""
        if not agent_name:
            agent_name = self.get_agent_name()
        
        agent_info = self.get_agent_registration(agent_name)
        if not agent_info:
            return False
        
        agent_info["last_active"] = datetime.now().isoformat()
        
        agent_dir = self.get_agents_dir() / agent_name
        registration_file = agent_dir / "registration.json"
        
        try:
            with open(registration_file, 'w', encoding='utf-8') as f:
                json.dump(agent_info, f, indent=2)
            return True
        except (IOError, json.JSONEncodeError):
            return False
    
    def is_agent_registered(self, agent_name: str) -> bool:
        """Check if an agent is registered."""
        return self.get_agent_registration(agent_name) is not None
    
    def unregister_agent(self, agent_name: str = None) -> bool:
        """Unregister an agent (remove registration)."""
        if not agent_name:
            agent_name = self.get_agent_name()
        
        agent_dir = self.get_agents_dir() / agent_name
        registration_file = agent_dir / "registration.json"
        
        try:
            if registration_file.exists():
                registration_file.unlink()
            
            # Remove agent directory if empty
            if agent_dir.exists() and not any(agent_dir.iterdir()):
                agent_dir.rmdir()
            
            return True
        except OSError:
            return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent management statistics."""
        agents = self.list_registered_agents()
        
        # Count active agents (registered in last 24 hours)
        now = datetime.now()
        active_count = 0
        
        for agent in agents:
            try:
                last_active = datetime.fromisoformat(agent["last_active"])
                if (now - last_active).total_seconds() < 86400:  # 24 hours
                    active_count += 1
            except (ValueError, KeyError):
                continue
        
        return {
            "total_agents": len(agents),
            "active_agents": active_count,
            "current_agent": self.get_agent_name(),
            "custom_name_set": self.custom_agent_name is not None,
            "messaging_root": str(self.messaging_root)
        }


# Global agent manager instance
_agent_manager = None


def get_agent_manager(messaging_root: Path = None) -> AgentManager:
    """Get or create the global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager(messaging_root)
    return _agent_manager


# Convenience functions for direct use
def get_agent_name() -> str:
    """Get current agent name."""
    return get_agent_manager().get_agent_name()


def register_agent() -> Dict[str, Any]:
    """Register current agent."""
    return get_agent_manager().register_agent()


def set_custom_agent_name(name: str):
    """Set custom agent name."""
    get_agent_manager().set_custom_agent_name(name)


def get_custom_agent_name() -> Optional[str]:
    """Get custom agent name if set."""
    return get_agent_manager().get_custom_agent_name()


def get_agent_registration(agent_name: str) -> Optional[Dict[str, Any]]:
    """Get agent registration information."""
    return get_agent_manager().get_agent_registration(agent_name)


def list_registered_agents() -> List[Dict[str, Any]]:
    """List all registered agents."""
    return get_agent_manager().list_registered_agents()


def update_agent_activity(agent_name: str = None) -> bool:
    """Update agent's last activity timestamp."""
    return get_agent_manager().update_agent_activity(agent_name)


def is_agent_registered(agent_name: str) -> bool:
    """Check if an agent is registered."""
    return get_agent_manager().is_agent_registered(agent_name)


def unregister_agent(agent_name: str = None) -> bool:
    """Unregister an agent."""
    return get_agent_manager().unregister_agent(agent_name)


def get_agent_stats() -> Dict[str, Any]:
    """Get agent management statistics."""
    return get_agent_manager().get_agent_stats()