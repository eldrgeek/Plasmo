#!/usr/bin/env python3
"""
Agent Notifications Module
==========================

Provides notification system functionality for the MCP server multi-agent system.

Features:
- Event-driven notifications
- Real-time notification delivery
- Notification queuing and persistence
- Wait/notify patterns for agent coordination
- Cancel flag support
- Thread-safe operations

"""

import asyncio
import json
import logging
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .agent_management import get_agent_manager

logger = logging.getLogger(__name__)


class NotificationManager:
    """Core notification functionality for inter-agent communication."""
    
    def __init__(self, messaging_root: Path = None):
        """Initialize notification manager with optional custom root directory."""
        self.messaging_root = messaging_root or Path.cwd() / "messages"
        self.notification_lock = threading.Lock()
        self.comm_hub = CommunicationHub()
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.messaging_root,
            self.messaging_root / "notifications",
            self.get_notifications_dir(),
            self.get_cancel_flags_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_notifications_dir(self) -> Path:
        """Get notifications directory."""
        return self.messaging_root / "notifications" / "pending"
    
    def get_cancel_flags_dir(self) -> Path:
        """Get cancel flags directory."""
        return self.messaging_root / "notifications" / "cancel_flags"
    
    def send_notification(self, target_agent: str, message: str, sender: str = None) -> Dict[str, Any]:
        """Send a notification to target agent."""
        if sender is None:
            agent_manager = get_agent_manager(self.messaging_root)
            sender = agent_manager.get_agent_name()
        
        notification_id = f"{int(time.time() * 1000000)}_{uuid.uuid4().hex[:8]}"
        
        notification_data = {
            "id": notification_id,
            "target_agent": target_agent,
            "message": message,
            "sender": sender,
            "timestamp": datetime.now().isoformat(),
            "created_at": time.time()
        }
        
        # Save notification atomically
        notification_file = self.get_notifications_dir() / f"{target_agent}_{notification_id}.json"
        temp_file = notification_file.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(notification_data, f, indent=2)
        
        temp_file.rename(notification_file)
        
        # Immediately wake up waiting agent (event-driven)
        try:
            asyncio.create_task(self.comm_hub.notify_agent(target_agent, "notification"))
        except RuntimeError:
            # No event loop running, notifications will be picked up by polling
            pass
        
        logger.info(f"Sent notification {notification_id} to {target_agent} from {sender}")
        return notification_data
    
    def get_pending_notifications(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get pending notifications for an agent."""
        notifications = []
        
        for notification_file in self.get_notifications_dir().glob(f"{agent_name}_*.json"):
            try:
                with open(notification_file, 'r', encoding='utf-8') as f:
                    notification_data = json.load(f)
                notifications.append(notification_data)
            except (json.JSONDecodeError, IOError):
                continue
        
        # Sort by creation time (oldest first)
        notifications.sort(key=lambda x: x.get("created_at", 0))
        return notifications
    
    def clear_notifications(self, agent_name: str, notification_ids: List[str] = None) -> int:
        """Clear specific notifications or all notifications for an agent."""
        cleared_count = 0
        
        if notification_ids:
            # Clear specific notifications
            for notification_id in notification_ids:
                notification_file = self.get_notifications_dir() / f"{agent_name}_{notification_id}.json"
                if notification_file.exists():
                    try:
                        notification_file.unlink()
                        cleared_count += 1
                    except OSError:
                        pass
        else:
            # Clear all notifications for agent
            for notification_file in self.get_notifications_dir().glob(f"{agent_name}_*.json"):
                try:
                    notification_file.unlink()
                    cleared_count += 1
                except OSError:
                    pass
        
        return cleared_count
    
    def set_cancel_flag(self, agent_name: str) -> bool:
        """Set cancel flag for an agent."""
        try:
            cancel_file = self.get_cancel_flags_dir() / f"{agent_name}.flag"
            cancel_file.write_text(str(time.time()))
            return True
        except OSError:
            return False
    
    def check_cancel_flag(self, agent_name: str) -> bool:
        """Check if cancel flag is set for an agent."""
        cancel_file = self.get_cancel_flags_dir() / f"{agent_name}.flag"
        return cancel_file.exists()
    
    def clear_cancel_flag(self, agent_name: str) -> bool:
        """Clear cancel flag for an agent."""
        cancel_file = self.get_cancel_flags_dir() / f"{agent_name}.flag"
        try:
            if cancel_file.exists():
                cancel_file.unlink()
            return True
        except OSError:
            return False
    
    def get_notification_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get notification statistics for an agent."""
        notifications = self.get_pending_notifications(agent_name)
        
        # Count notifications by sender
        sender_counts = {}
        for notification in notifications:
            sender = notification.get("sender", "unknown")
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        return {
            "pending_notifications": len(notifications),
            "sender_counts": sender_counts,
            "has_cancel_flag": self.check_cancel_flag(agent_name),
            "agent_name": agent_name
        }


class CommunicationHub:
    """Event-driven communication hub for immediate multi-agent coordination."""
    
    def __init__(self):
        self.waiting_agents = {}  # agent_name -> asyncio.Event
        self.agent_timeouts = {}  # agent_name -> timeout_handle
        self._lock = asyncio.Lock()
    
    async def wait_for_notifications(self, agent_name: str, notification_manager: NotificationManager, 
                                   timeout: float = None) -> Dict[str, Any]:
        """Wait for notifications for an agent."""
        start_time = time.time()
        
        # Check for existing notifications first
        existing_notifications = notification_manager.get_pending_notifications(agent_name)
        if existing_notifications:
            # Clear delivered notifications
            delivered_ids = [n["id"] for n in existing_notifications]
            notification_manager.clear_notifications(agent_name, delivered_ids)
            
            return {
                "success": True,
                "operation": "wait_for_notifications",
                "notifications": existing_notifications,
                "count": len(existing_notifications),
                "wait_time": 0,
                "delivery_type": "immediate",
                "agent_name": agent_name
            }
        
        # Set up event-driven waiting
        async with self._lock:
            event = asyncio.Event()
            self.waiting_agents[agent_name] = event
            
            # Set up timeout if specified
            timeout_handle = None
            if timeout:
                timeout_handle = asyncio.create_task(asyncio.sleep(timeout))
                self.agent_timeouts[agent_name] = timeout_handle
        
        try:
            logger.info(f"Agent {agent_name} starting event-driven wait for notifications...")
            
            # Wait for either notification event or timeout
            if timeout:
                done, pending = await asyncio.wait(
                    [asyncio.create_task(event.wait()), timeout_handle],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
                
                # Check if timeout occurred
                if timeout_handle in done:
                    return {
                        "success": False,
                        "operation": "wait_for_notifications",
                        "error": f"Wait timeout after {timeout} seconds",
                        "wait_time": round(time.time() - start_time, 1),
                        "agent_name": agent_name
                    }
            else:
                # Wait indefinitely
                await event.wait()
            
            # Get notifications after being woken up
            wait_time = time.time() - start_time
            notifications = notification_manager.get_pending_notifications(agent_name)
            
            # Clear delivered notifications
            if notifications:
                delivered_ids = [n["id"] for n in notifications]
                notification_manager.clear_notifications(agent_name, delivered_ids)
            
            logger.info(f"Agent {agent_name} received {len(notifications)} notifications after {wait_time:.3f}s")
            
            return {
                "success": True,
                "operation": "wait_for_notifications",
                "notifications": notifications,
                "count": len(notifications),
                "wait_time": round(wait_time, 3),
                "delivery_type": "event_driven",
                "agent_name": agent_name
            }
            
        finally:
            # Clean up waiting agent
            async with self._lock:
                self.waiting_agents.pop(agent_name, None)
                if agent_name in self.agent_timeouts:
                    timeout_handle = self.agent_timeouts.pop(agent_name)
                    if not timeout_handle.done():
                        timeout_handle.cancel()
    
    async def notify_agent(self, agent_name: str, communication_type: str = "notification"):
        """Immediately wake up a waiting agent."""
        async with self._lock:
            if agent_name in self.waiting_agents:
                event = self.waiting_agents[agent_name]
                event.set()
                logger.info(f"Immediately woke up agent {agent_name} for {communication_type}")
                return True
            return False
    
    async def cancel_wait(self, agent_name: str) -> bool:
        """Cancel waiting for a specific agent."""
        async with self._lock:
            if agent_name in self.waiting_agents:
                event = self.waiting_agents[agent_name]
                event.set()
                logger.info(f"Cancelled wait for agent {agent_name}")
                return True
            return False
    
    def get_waiting_agents(self) -> List[str]:
        """Get list of currently waiting agents."""
        return list(self.waiting_agents.keys())


# Global notification manager instance
_notification_manager = None


def get_notification_manager(messaging_root: Path = None) -> NotificationManager:
    """Get or create the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager(messaging_root)
    return _notification_manager


# Convenience functions for direct use
def send_notification(target_agent: str, message: str, sender: str = None) -> Dict[str, Any]:
    """Send a notification to target agent."""
    return get_notification_manager().send_notification(target_agent, message, sender)


def get_pending_notifications(agent_name: str) -> List[Dict[str, Any]]:
    """Get pending notifications for an agent."""
    return get_notification_manager().get_pending_notifications(agent_name)


def clear_notifications(agent_name: str, notification_ids: List[str] = None) -> int:
    """Clear notifications for an agent."""
    return get_notification_manager().clear_notifications(agent_name, notification_ids)


def set_cancel_flag(agent_name: str) -> bool:
    """Set cancel flag for an agent."""
    return get_notification_manager().set_cancel_flag(agent_name)


def check_cancel_flag(agent_name: str) -> bool:
    """Check if cancel flag is set for an agent."""
    return get_notification_manager().check_cancel_flag(agent_name)


def clear_cancel_flag(agent_name: str) -> bool:
    """Clear cancel flag for an agent."""
    return get_notification_manager().clear_cancel_flag(agent_name)


def get_notification_stats(agent_name: str) -> Dict[str, Any]:
    """Get notification statistics for an agent."""
    return get_notification_manager().get_notification_stats(agent_name)


async def wait_for_notifications(agent_name: str, timeout: float = None) -> Dict[str, Any]:
    """Wait for notifications for an agent."""
    notification_manager = get_notification_manager()
    return await notification_manager.comm_hub.wait_for_notifications(agent_name, notification_manager, timeout)