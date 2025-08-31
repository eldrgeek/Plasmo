#!/usr/bin/env python3
"""
Agent Messaging System
======================

Extracted inter-agent messaging functionality from the main MCP server.
Provides clean interface for multi-agent communication and coordination.

Features:
- Message creation and delivery
- Agent registration and discovery
- Notification system with event-driven support
- File sharing between agents
- Thread-safe operations
- Persistent storage

"""

import asyncio
import json
import logging
import os
import shutil
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AgentMessaging:
    """Multi-agent messaging system for MCP server coordination."""
    
    def __init__(self, messaging_root: Path = None):
        """Initialize messaging system with optional custom root directory."""
        self.messaging_root = messaging_root or Path.cwd() / "messages"
        self.custom_agent_name = None
        self.message_lock = threading.Lock()
        self.notification_lock = threading.Lock()
        self.comm_hub = CommunicationHub()
        
        # Ensure directories exist
        self.ensure_messaging_directories()
    
    def get_messaging_root(self) -> Path:
        """Get messaging root directory."""
        return self.messaging_root
    
    def get_agents_dir(self) -> Path:
        """Get agents directory."""
        return self.messaging_root / "agents"
    
    def get_messages_dir(self) -> Path:
        """Get messages directory."""
        return self.messaging_root / "messages"
    
    def get_deleted_dir(self) -> Path:
        """Get deleted messages directory."""
        return self.messaging_root / "deleted"
    
    def get_notifications_dir(self) -> Path:
        """Get notifications directory."""
        return self.messaging_root / "notifications" / "pending"
    
    def get_cancel_flags_dir(self) -> Path:
        """Get cancel flags directory."""
        return self.messaging_root / "notifications" / "cancel_flags"
    
    def get_sequence_file(self) -> Path:
        """Get sequence file path."""
        return self.messaging_root / "sequence.txt"
    
    def ensure_messaging_directories(self):
        """Ensure all messaging directories exist."""
        directories = [
            self.messaging_root,
            self.get_agents_dir(),
            self.get_messages_dir(),
            self.get_deleted_dir(),
            self.messaging_root / "notifications",
            self.get_notifications_dir(),
            self.get_cancel_flags_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize sequence file if it doesn't exist
        sequence_file = self.get_sequence_file()
        if not sequence_file.exists():
            sequence_file.write_text("0")
    
    def set_custom_agent_name(self, name: str):
        """Set custom agent name."""
        self.custom_agent_name = name
    
    def get_custom_agent_name(self) -> Optional[str]:
        """Get custom agent name."""
        return self.custom_agent_name
    
    def get_agent_name(self) -> str:
        """Get agent name - custom name if set, otherwise current directory name."""
        if self.custom_agent_name:
            return self.custom_agent_name
        return Path.cwd().name
    
    def get_next_message_id(self) -> int:
        """Get next message ID atomically."""
        with self.message_lock:
            sequence_file = self.get_sequence_file()
            try:
                current_id = int(sequence_file.read_text().strip())
                next_id = current_id + 1
                sequence_file.write_text(str(next_id))
                return next_id
            except (ValueError, FileNotFoundError):
                sequence_file.write_text("1")
                return 1
    
    def register_agent(self) -> Dict[str, Any]:
        """Register current agent in the messaging system."""
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
    
    def create_message(self, to: str, subject: str, message: str, reply_to: Optional[int] = None) -> Dict[str, Any]:
        """Create a new message."""
        message_id = self.get_next_message_id()
        from_agent = self.get_agent_name()
        
        message_data = {
            "id": message_id,
            "to": to,
            "from": from_agent,
            "subject": subject,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "read": False,
            "reply_to": reply_to
        }
        
        # Save message
        message_file = self.get_messages_dir() / f"{message_id}.json"
        with open(message_file, 'w', encoding='utf-8') as f:
            json.dump(message_data, f, indent=2)
        
        # Update sender's last active timestamp
        self.register_agent()
        
        return message_data
    
    def get_messages(self, agent_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get messages for an agent with optional filtering."""
        messages = []
        
        # Read all message files
        for message_file in self.get_messages_dir().glob("*.json"):
            try:
                with open(message_file, 'r', encoding='utf-8') as f:
                    message_data = json.load(f)
                
                # Check if message is for this agent
                if message_data.get("to") != agent_name:
                    continue
                
                # Apply filters if provided
                if filters:
                    if "id" in filters and message_data.get("id") != filters["id"]:
                        continue
                    if "from" in filters and message_data.get("from") != filters["from"]:
                        continue
                    if "subject_contains" in filters and filters["subject_contains"].lower() not in message_data.get("subject", "").lower():
                        continue
                    if "unread_only" in filters and filters["unread_only"] and message_data.get("read", False):
                        continue
                    if "after" in filters:
                        try:
                            msg_time = datetime.fromisoformat(message_data.get("timestamp", ""))
                            filter_time = datetime.fromisoformat(filters["after"])
                            if msg_time <= filter_time:
                                continue
                        except ValueError:
                            continue
                    if "before" in filters:
                        try:
                            msg_time = datetime.fromisoformat(message_data.get("timestamp", ""))
                            filter_time = datetime.fromisoformat(filters["before"])
                            if msg_time >= filter_time:
                                continue
                        except ValueError:
                            continue
                
                messages.append(message_data)
                
            except (json.JSONDecodeError, IOError):
                continue
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return messages
    
    def mark_message_read(self, message_id: int, agent_name: str) -> bool:
        """Mark a message as read."""
        message_file = self.get_messages_dir() / f"{message_id}.json"
        
        if not message_file.exists():
            return False
        
        try:
            with open(message_file, 'r', encoding='utf-8') as f:
                message_data = json.load(f)
            
            # Only allow the recipient to mark as read
            if message_data.get("to") != agent_name:
                return False
            
            message_data["read"] = True
            message_data["read_timestamp"] = datetime.now().isoformat()
            
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump(message_data, f, indent=2)
            
            return True
            
        except (json.JSONDecodeError, IOError):
            return False
    
    def delete_message(self, message_id: int, agent_name: str) -> bool:
        """Delete a message (move to deleted folder). Only sender can delete."""
        message_file = self.get_messages_dir() / f"{message_id}.json"
        
        if not message_file.exists():
            return False
        
        try:
            with open(message_file, 'r', encoding='utf-8') as f:
                message_data = json.load(f)
            
            # Only allow the sender to delete
            if message_data.get("from") != agent_name:
                return False
            
            # Move to deleted folder
            deleted_file = self.get_deleted_dir() / f"{message_id}.json"
            shutil.move(str(message_file), str(deleted_file))
            
            return True
            
        except (json.JSONDecodeError, IOError):
            return False
    
    def read_agent_file(self, agent_name: str, file_path: str) -> Optional[str]:
        """Read a file from another agent's repository."""
        try:
            # Get agent registration to find their working directory
            agent_info = self.get_agent_registration(agent_name)
            if not agent_info:
                return None
            
            agent_working_dir = Path(agent_info["working_directory"])
            target_file = agent_working_dir / file_path
            
            # Security check: ensure the file is within the agent's working directory
            try:
                target_file.resolve().relative_to(agent_working_dir.resolve())
            except ValueError:
                # Path is outside the agent's working directory
                return None
            
            if not target_file.exists() or not target_file.is_file():
                return None
            
            with open(target_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception:
            return None
    
    # Notification System
    def create_notification(self, target_agent: str, message: str, sender: str = None) -> Dict[str, Any]:
        """Create a notification for target agent."""
        if sender is None:
            sender = self.get_agent_name()
        
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
        asyncio.create_task(self.comm_hub.notify_agent(target_agent, "notification"))
        
        logger.info(f"Created notification {notification_id} for {target_agent} from {sender}")
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
    
    def delete_notifications(self, agent_name: str, notification_ids: List[str]):
        """Delete specific notifications for an agent."""
        for notification_id in notification_ids:
            notification_file = self.get_notifications_dir() / f"{agent_name}_{notification_id}.json"
            if notification_file.exists():
                try:
                    notification_file.unlink()
                except OSError:
                    pass
    
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


class CommunicationHub:
    """Event-driven communication hub for immediate multi-agent coordination."""
    
    def __init__(self):
        self.waiting_agents = {}  # agent_name -> asyncio.Event
        self.agent_timeouts = {}  # agent_name -> timeout_handle
        self._lock = asyncio.Lock()
    
    async def wait_for_communication(self, agent_name: str, messaging: AgentMessaging, 
                                   include_messages: bool = False, timeout: float = None) -> Dict[str, Any]:
        """Wait for any communication (notifications and optionally messages) for an agent."""
        start_time = time.time()
        
        # Check for existing communications first
        existing_comms = await self._get_existing_communications(agent_name, messaging, include_messages)
        if existing_comms["has_communications"]:
            return {
                "success": True,
                "operation": "wait",
                "notifications": existing_comms["notifications"],
                "messages": existing_comms["messages"],
                "count": existing_comms["total_count"],
                "wait_time": 0,
                "delivery_type": "immediate",
                "agent_name": agent_name,
                "unified_delivery": include_messages
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
            logger.info(f"Agent {agent_name} starting event-driven wait for communications...")
            
            # Wait for either communication event or timeout
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
                        "operation": "wait",
                        "error": f"Wait timeout after {timeout} seconds",
                        "wait_time": round(time.time() - start_time, 1),
                        "agent_name": agent_name
                    }
            else:
                # Wait indefinitely
                await event.wait()
            
            # Get communications after being woken up
            wait_time = time.time() - start_time
            comms = await self._get_existing_communications(agent_name, messaging, include_messages)
            
            logger.info(f"Agent {agent_name} received {comms['total_count']} communications after {wait_time:.3f}s")
            
            return {
                "success": True,
                "operation": "wait",
                "notifications": comms["notifications"],
                "messages": comms["messages"],
                "count": comms["total_count"],
                "wait_time": round(wait_time, 3),
                "delivery_type": "event_driven",
                "agent_name": agent_name,
                "unified_delivery": include_messages
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
    
    async def _get_existing_communications(self, agent_name: str, messaging: AgentMessaging, 
                                        include_messages: bool) -> Dict[str, Any]:
        """Get existing notifications and optionally messages for an agent."""
        notifications = messaging.get_pending_notifications(agent_name)
        messages = []
        
        if include_messages:
            messages = messaging.get_messages(agent_name, {"unread_only": True})
        
        # Clean up delivered communications
        if notifications:
            delivered_ids = [n["id"] for n in notifications]
            messaging.delete_notifications(agent_name, delivered_ids)
        
        if messages:
            for msg in messages:
                messaging.mark_message_read(msg["id"], agent_name)
        
        return {
            "notifications": notifications,
            "messages": messages,
            "total_count": len(notifications) + len(messages),
            "has_communications": len(notifications) > 0 or len(messages) > 0
        }
    
    def get_waiting_agents(self) -> List[str]:
        """Get list of currently waiting agents."""
        return list(self.waiting_agents.keys())


def create_messaging_tools(mcp, messaging: AgentMessaging):
    """Create MCP tools for the messaging system."""
    
    @mcp.tool()
    def register_agent_with_name(agent_name: str) -> Dict[str, Any]:
        """Register current agent with a custom name for multi-agent coordination."""
        try:
            # Set the custom agent name
            messaging.set_custom_agent_name(agent_name)
            
            # Register with the messaging system using the new name
            registration_info = messaging.register_agent()
            
            return {
                "success": True,
                "operation": "register_with_custom_name", 
                "agent_name": agent_name,
                "previous_name": Path.cwd().name,
                "registration": registration_info,
                "message": f"Agent successfully registered as '{agent_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": "register_agent_with_name"
            }
    
    @mcp.tool()
    def get_current_agent_name() -> Dict[str, Any]:
        """Get the current agent name being used for messaging."""
        return {
            "success": True,
            "agent_name": messaging.get_agent_name(),
            "custom_name": messaging.get_custom_agent_name(),
            "is_custom": messaging.get_custom_agent_name() is not None
        }
    
    @mcp.tool()
    def messages(operation: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Multi-agent messaging system for communication between MCP server instances."""
        try:
            current_agent = messaging.get_agent_name()
            
            if operation == "send":
                if not payload or not all(k in payload for k in ["to", "subject", "message"]):
                    return {
                        "success": False,
                        "error": "send operation requires payload with 'to', 'subject', and 'message'"
                    }
                
                # Check if target agent is registered
                target_agent = payload["to"]
                if not messaging.get_agent_registration(target_agent):
                    return {
                        "success": False,
                        "error": f"Target agent '{target_agent}' is not registered"
                    }
                
                message_data = messaging.create_message(
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
                messages_list = messaging.get_messages(current_agent, filters)
                
                # Mark first unread message as read if no specific filters
                if not filters and messages_list:
                    unread_messages = [m for m in messages_list if not m.get("read", False)]
                    if unread_messages:
                        messaging.mark_message_read(unread_messages[0]["id"], current_agent)
                        unread_messages[0]["read"] = True
                
                return {
                    "success": True,
                    "operation": "get",
                    "agent": current_agent,
                    "messages": messages_list
                }
            
            elif operation == "list":
                filters = payload or {}
                messages_list = messaging.get_messages(current_agent, filters)
                
                # Return summary information only
                summaries = []
                for msg in messages_list:
                    summary = {
                        "id": msg["id"],
                        "from": msg["from"],
                        "subject": msg["subject"],
                        "timestamp": msg["timestamp"],
                        "read": msg.get("read", False)
                    }
                    if msg.get("reply_to"):
                        summary["reply_to"] = msg["reply_to"]
                    summaries.append(summary)
                
                return {
                    "success": True,
                    "operation": "list",
                    "agent": current_agent,
                    "message_summaries": summaries,
                    "total_count": len(summaries),
                    "unread_count": len([m for m in summaries if not m["read"]])
                }
            
            elif operation == "delete":
                if not payload or "id" not in payload:
                    return {
                        "success": False,
                        "error": "delete operation requires payload with 'id'"
                    }
                
                success = messaging.delete_message(payload["id"], current_agent)
                return {
                    "success": success,
                    "operation": "delete",
                    "message_id": payload["id"],
                    "deleted": success
                }
            
            elif operation == "reply":
                if not payload or not all(k in payload for k in ["reply_to", "message"]):
                    return {
                        "success": False,
                        "error": "reply operation requires payload with 'reply_to' and 'message'"
                    }
                
                # Get original message to determine recipient and subject
                original_messages = messaging.get_messages(current_agent, {"id": payload["reply_to"]})
                if not original_messages:
                    # Check if we sent the original message
                    try:
                        message_file = messaging.get_messages_dir() / f"{payload['reply_to']}.json"
                        if message_file.exists():
                            with open(message_file, 'r', encoding='utf-8') as f:
                                original_message = json.load(f)
                            if original_message.get("from") == current_agent:
                                original_messages = [original_message]
                    except (json.JSONDecodeError, IOError):
                        pass
                
                if not original_messages:
                    return {
                        "success": False,
                        "error": f"Original message {payload['reply_to']} not found"
                    }
                
                original = original_messages[0]
                reply_to_agent = original["from"] if original["to"] == current_agent else original["to"]
                reply_subject = f"Re: {original['subject']}" if not original["subject"].startswith("Re: ") else original["subject"]
                
                message_data = messaging.create_message(
                    to=reply_to_agent,
                    subject=reply_subject,
                    message=payload["message"],
                    reply_to=payload["reply_to"]
                )
                
                return {
                    "success": True,
                    "operation": "reply",
                    "message_id": message_data["id"],
                    "reply_to": payload["reply_to"],
                    "message": message_data
                }
            
            elif operation == "register":
                registration_info = messaging.register_agent()
                return {
                    "success": True,
                    "operation": "register",
                    "agent": registration_info
                }
            
            elif operation == "agents":
                agents_list = messaging.list_registered_agents()
                return {
                    "success": True,
                    "operation": "agents",
                    "agents": agents_list,
                    "total_count": len(agents_list)
                }
            
            elif operation == "read_file":
                if not payload or not all(k in payload for k in ["agent", "file_path"]):
                    return {
                        "success": False,
                        "error": "read_file operation requires payload with 'agent' and 'file_path'"
                    }
                
                file_content = messaging.read_agent_file(payload["agent"], payload["file_path"])
                if file_content is None:
                    return {
                        "success": False,
                        "error": f"Could not read file '{payload['file_path']}' from agent '{payload['agent']}'"
                    }
                
                return {
                    "success": True,
                    "operation": "read_file",
                    "agent": payload["agent"],
                    "file_path": payload["file_path"],
                    "content": file_content
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["send", "get", "list", "delete", "reply", "register", "agents", "read_file"]
                }
        
        except Exception as e:
            logger.error(f"Error in messages operation: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }
    
    @mcp.tool()
    async def notify(operation: str, target_agent: str = None, message: str = None, 
                    sender: str = None, agent_name: str = None) -> Dict[str, Any]:
        """Clean notification system for multi-agent coordination."""
        try:
            # For backward compatibility, fall back to directory-based name if not provided
            current_agent = agent_name if agent_name else messaging.get_agent_name()
            
            if operation == "notify":
                if not target_agent or not message:
                    return {
                        "success": False,
                        "error": "notify operation requires 'target_agent' and 'message'"
                    }
                
                notification = messaging.create_notification(target_agent, message, sender)
                
                return {
                    "success": True,
                    "operation": "notify",
                    "notification_id": notification["id"],
                    "target_agent": target_agent,
                    "message": message,
                    "sender": notification["sender"],
                    "timestamp": notification["timestamp"]
                }
            
            elif operation == "wait":
                if not agent_name:
                    return {
                        "success": False,
                        "error": "wait operation requires 'agent_name' parameter"
                    }
                
                logger.info(f"Agent {current_agent} starting event-driven wait for notifications...")
                
                # Use event-driven waiting instead of polling
                result = await messaging.comm_hub.wait_for_communication(
                    current_agent, messaging, include_messages=False
                )
                return result
            
            elif operation == "cancel_wait":
                if not target_agent:
                    return {
                        "success": False,
                        "error": "cancel_wait operation requires 'target_agent'"
                    }
                
                success = messaging.set_cancel_flag(target_agent)
                
                return {
                    "success": success,
                    "operation": "cancel_wait",
                    "target_agent": target_agent,
                    "message": f"Cancel signal sent to {target_agent}" if success else "Failed to send cancel signal"
                }
            
            elif operation == "check":
                if not agent_name:
                    return {
                        "success": False,
                        "error": "check operation requires 'agent_name' parameter"
                    }
                
                notifications = messaging.get_pending_notifications(current_agent)
                
                return {
                    "success": True,
                    "operation": "check",
                    "notifications": notifications,
                    "count": len(notifications),
                    "has_pending": len(notifications) > 0,
                    "agent_name": current_agent
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "available_operations": ["notify", "wait", "cancel_wait", "check"]
                }
        
        except Exception as e:
            logger.error(f"Notification operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            } 