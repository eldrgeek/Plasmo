#!/usr/bin/env python3
"""
Agent Messaging Module
======================

Provides inter-agent messaging functionality for the MCP server multi-agent system.

Features:
- Message creation and delivery
- Message filtering and search
- Message status management (read/unread)
- Message threading (reply support)
- File-based persistent storage
- Thread-safe operations

"""

import json
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .agent_management import get_agent_manager


class MessageManager:
    """Core messaging functionality for inter-agent communication."""
    
    def __init__(self, messaging_root: Path = None):
        """Initialize message manager with optional custom root directory."""
        self.messaging_root = messaging_root or Path.cwd() / "messages"
        self.message_lock = threading.Lock()
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.messaging_root,
            self.get_messages_dir(),
            self.get_deleted_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize sequence file if it doesn't exist
        sequence_file = self.get_sequence_file()
        if not sequence_file.exists():
            sequence_file.write_text("0")
    
    def get_messages_dir(self) -> Path:
        """Get messages directory."""
        return self.messaging_root / "messages"
    
    def get_deleted_dir(self) -> Path:
        """Get deleted messages directory."""
        return self.messaging_root / "deleted"
    
    def get_sequence_file(self) -> Path:
        """Get sequence file path."""
        return self.messaging_root / "sequence.txt"
    
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
    
    def create_message(self, to: str, subject: str, message: str, reply_to: Optional[int] = None) -> Dict[str, Any]:
        """Create a new message."""
        message_id = self.get_next_message_id()
        agent_manager = get_agent_manager(self.messaging_root)
        from_agent = agent_manager.get_agent_name()
        
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
        agent_manager.update_agent_activity()
        
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
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific message by ID."""
        message_file = self.get_messages_dir() / f"{message_id}.json"
        
        if not message_file.exists():
            return None
        
        try:
            with open(message_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
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
    
    def list_message_summaries(self, agent_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List message summaries for an agent."""
        messages = self.get_messages(agent_name, filters)
        
        summaries = []
        for msg in messages:
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
        
        return summaries
    
    def search_messages(self, agent_name: str, query: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search messages for an agent."""
        if not search_fields:
            search_fields = ["subject", "message", "from"]
        
        messages = self.get_messages(agent_name)
        results = []
        
        query_lower = query.lower()
        
        for msg in messages:
            match_found = False
            for field in search_fields:
                if field in msg and query_lower in str(msg[field]).lower():
                    match_found = True
                    break
            
            if match_found:
                results.append(msg)
        
        return results
    
    def get_message_thread(self, message_id: int, agent_name: str) -> List[Dict[str, Any]]:
        """Get a message thread (original message and all replies)."""
        thread_messages = []
        
        # Find the original message
        original_msg = self.get_message_by_id(message_id)
        if not original_msg:
            return thread_messages
        
        # If this is a reply, find the original
        if original_msg.get("reply_to"):
            original_msg = self.get_message_by_id(original_msg["reply_to"])
            if not original_msg:
                return thread_messages
        
        # Only show thread if agent is participant
        if original_msg.get("to") != agent_name and original_msg.get("from") != agent_name:
            return thread_messages
        
        thread_messages.append(original_msg)
        
        # Find all replies to this message
        for message_file in self.get_messages_dir().glob("*.json"):
            try:
                with open(message_file, 'r', encoding='utf-8') as f:
                    msg_data = json.load(f)
                
                if msg_data.get("reply_to") == original_msg["id"]:
                    # Only include if agent is participant
                    if msg_data.get("to") == agent_name or msg_data.get("from") == agent_name:
                        thread_messages.append(msg_data)
                
            except (json.JSONDecodeError, IOError):
                continue
        
        # Sort by timestamp
        thread_messages.sort(key=lambda x: x.get("timestamp", ""))
        return thread_messages
    
    def get_message_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get message statistics for an agent."""
        messages = self.get_messages(agent_name)
        
        total_messages = len(messages)
        unread_messages = len([m for m in messages if not m.get("read", False)])
        
        # Count messages by sender
        sender_counts = {}
        for msg in messages:
            sender = msg.get("from", "unknown")
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        return {
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "read_messages": total_messages - unread_messages,
            "sender_counts": sender_counts,
            "agent_name": agent_name
        }


# Global message manager instance
_message_manager = None


def get_message_manager(messaging_root: Path = None) -> MessageManager:
    """Get or create the global message manager instance."""
    global _message_manager
    if _message_manager is None:
        _message_manager = MessageManager(messaging_root)
    return _message_manager


# Convenience functions for direct use
def create_message(to: str, subject: str, message: str, reply_to: Optional[int] = None) -> Dict[str, Any]:
    """Create a new message."""
    return get_message_manager().create_message(to, subject, message, reply_to)


def get_messages(agent_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get messages for an agent with optional filtering."""
    return get_message_manager().get_messages(agent_name, filters)


def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific message by ID."""
    return get_message_manager().get_message_by_id(message_id)


def mark_message_read(message_id: int, agent_name: str) -> bool:
    """Mark a message as read."""
    return get_message_manager().mark_message_read(message_id, agent_name)


def delete_message(message_id: int, agent_name: str) -> bool:
    """Delete a message."""
    return get_message_manager().delete_message(message_id, agent_name)


def list_message_summaries(agent_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """List message summaries for an agent."""
    return get_message_manager().list_message_summaries(agent_name, filters)


def search_messages(agent_name: str, query: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
    """Search messages for an agent."""
    return get_message_manager().search_messages(agent_name, query, search_fields)


def get_message_thread(message_id: int, agent_name: str) -> List[Dict[str, Any]]:
    """Get a message thread."""
    return get_message_manager().get_message_thread(message_id, agent_name)


def get_message_stats(agent_name: str) -> Dict[str, Any]:
    """Get message statistics for an agent."""
    return get_message_manager().get_message_stats(agent_name)