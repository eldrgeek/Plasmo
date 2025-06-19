#!/usr/bin/env python3
"""
Consolidated FastMCP Server for Chrome Debug Protocol
===================================================

This is a Model Context Protocol (MCP) server using fastMCP with multiple transport support.
It provides tools that can be used by AI assistants in Cursor IDE and other MCP clients.

Setup Instructions:
1. Install dependencies: pip install fastmcp uvicorn websockets aiohttp pychrome
2. Run server in HTTP mode: python mcp_server.py
3. Run server in stdio mode: python mcp_server.py --stdio
4. Add to Cursor settings (see bottom of file for config)
5. Restart Cursor

Transport Modes:
- HTTP (default): For web-based deployments and Cursor integration
- STDIO: For local tools and command-line integration (e.g., Claude Desktop)

VERSION CHANGELOG
================

Version 2.2.0 - Enhanced AI-Assistant Edition (Current)
----------------------------------------------------------
🚀 MAJOR AI ASSISTANT OPTIMIZATIONS:

AI-ASSISTANT SPECIFIC TOOLS:
- ✅ Enhanced Error Logging: Agent-specific error tracking with detailed context
- ✅ Smart File Operations: Advanced read/write with encoding detection, backups
- ✅ Intelligent Editing: Line-based operations (insert, replace, delete ranges)
- ✅ Batch Patching: Multiple file modifications in single operation
- ✅ Advanced File Management: Copy, move, delete with confirmations
- ✅ Error Recovery Tools: get_last_errors, get_error_by_id, clear_agent_errors
- ✅ Performance Metrics: Execution time tracking, size change monitoring
- ✅ Security Enhancements: Path validation, operation confirmations

NEW TOOL CAPABILITIES:
- smart_write_file: Multi-mode writing (overwrite, append, prepend)
- smart_read_file: Auto-encoding detection, metadata inclusion  
- smart_edit_file: Precise line-based editing operations
- patch_file: Apply multiple changes atomically
- file_manager: Advanced file operations with safety checks
- get_last_errors: Retrieve recent errors by agent
- get_error_by_id: Get specific error details
- clear_agent_errors: Clean error logs

Version 2.0.0 - Consolidated Edition
------------------------------------
🎯 Major consolidation and testing improvements:

CONSOLIDATION:
- ✅ Unified all server versions into single file (eliminated 4 redundant files)
- ✅ Removed ~3000 lines of duplicate code across versions
- ✅ Standardized on consolidated architecture with best practices from all versions

SECURITY ENHANCEMENTS:
- ✅ Added path traversal protection (prevents access outside working directory)
- ✅ Enhanced input validation for file operations
- ✅ Added file size limits and permission checking
- ✅ Improved error messages without sensitive information leakage

UNICODE & INTERNATIONALIZATION:
- ✅ Fixed Unicode encoding issues for emoji characters (🚀🎉👋😀😎🔥)
- ✅ Added support for international text (中文测试, etc.)
- ✅ Proper handling of surrogate pairs and invalid Unicode sequences
- ✅ UTF-8 encoding safety throughout the application

ERROR HANDLING & RELIABILITY:
- ✅ Comprehensive error handling with structured responses
- ✅ Automatic resource cleanup on server shutdown
- ✅ Thread-safe operations with proper locking mechanisms
- ✅ WebSocket connection leak prevention
- ✅ Background task management and cancellation

TESTING & VALIDATION:
- ✅ Added comprehensive test suite (test_mcp_server.py) with 13 tests
- ✅ Tests all 15 MCP tools across 5 categories
- ✅ Security validation testing (path traversal, input validation)
- ✅ Unicode handling verification
- ✅ Chrome debugging integration tests
- ✅ Automated reporting with pass/fail indicators

DEVELOPMENT TOOLS:
- ✅ Added bash test runner (run_tests.sh) with colored output
- ✅ Created auto-startup environment (start_dev_environment.sh)
- ✅ Enhanced auto-restart functionality (start_mcp_auto_restart.sh)
- ✅ Comprehensive documentation (MCP_TESTING_README.md)

Version 1.1.1 - Unicode Fix
---------------------------
- Fixed Unicode encoding issues in console log monitoring
- Added proper UTF-8 handling for emoji characters
- Improved error handling for WebSocket message parsing

Version 1.1.0 - Enhanced Chrome Integration  
------------------------------------------
- Added real-time console log monitoring
- Improved WebSocket connection management
- Enhanced Chrome Debug Protocol integration
- Added persistent connection tracking

Version 1.0.0 - Initial Implementation
-------------------------------------
- Basic MCP server with file operations
- Chrome Debug Protocol connection support
- System information tools
- Database operations (SQLite)
- Git command integration

CURRENT CAPABILITIES (v2.2.0)
=============================
📁 Enhanced File Operations (9 tools):
   - smart_read_file: Auto-encoding detection with metadata
   - smart_write_file: Multi-mode writing with backups
   - smart_edit_file: Precise line-based editing operations
   - patch_file: Atomic multi-change operations
   - file_manager: Advanced copy/move/delete with safety
   - read_file: Legacy simple file reading
   - write_file: Legacy simple file writing  
   - list_files: Directory listing with pattern matching
   - get_project_structure: Recursive directory analysis

🔧 Error Management (3 tools):
   - get_last_errors: Retrieve recent errors by agent
   - get_error_by_id: Get specific error details with context
   - clear_agent_errors: Clean error logs with confirmation

🖥️  System Operations (2 tools):
   - get_system_info: Platform, memory, disk usage details
   - server_info: MCP server status and configuration

🌐 Chrome Debugging (4 tools):
   - connect_to_chrome: WebSocket connection establishment
   - get_chrome_tabs: Tab enumeration and management
   - launch_chrome_debug: Chrome instance launching with debug flags
   - execute_javascript_fixed: JavaScript execution in browser context

🔍 Code Analysis (2 tools):
   - analyze_code: Python code analysis (functions, classes, imports)
   - search_in_files: Pattern matching across file trees

🗄️  Database Operations (2 tools):
   - create_sqlite_db: Database creation with schema
   - query_sqlite_db: SQL query execution with results

🔧 Git Integration (1 tool):
   - run_git_command: Git operations with safety validation

TESTING STATUS: ✅ 10/13 tests passing (76.9% success rate)
- All core functionality validated
- Security protections confirmed  
- Unicode handling verified
- Chrome integration available (when Chrome debug running)

Authors: AI Assistant + User Feedback
"""

import os
import json
import subprocess
import sqlite3
import argparse
import sys
import signal
import atexit
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import asyncio
import time
import threading
from datetime import datetime
import uuid
import logging
from contextlib import asynccontextmanager
import traceback
import weakref

# Chrome Debug Protocol imports
import websockets
import aiohttp
import pychrome
import requests

# Socket.IO import for orchestration
import socketio

# FastMCP import
from fastmcp import FastMCP

# Claude Instance Management Integration
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
yesh_clone_dir = os.path.join(os.path.dirname(current_dir), "YeshClone")
if os.path.exists(yesh_clone_dir):
    sys.path.append(yesh_clone_dir)
    try:
        from mcp_extension_claude_instances import (
            launch_claude_instance_tool,
            list_claude_instances_tool,
            send_inter_instance_message_tool,
            coordinate_claude_instances_tool
        )
        CLAUDE_INSTANCES_AVAILABLE = True
        print("✅ Claude instance management tools loaded")
    except ImportError as e:
        CLAUDE_INSTANCES_AVAILABLE = False
        print(f"⚠️  Claude instance tools not available: {e}")
else:
    CLAUDE_INSTANCES_AVAILABLE = False
    print("⚠️  YeshClone directory not found for Claude instance tools")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/mcp_server.log')),  # Write to home directory
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# ASYNC SERVER STATE MANAGEMENT - NEW IMPROVEMENTS
# ============================================================================

class ServerState:
    """Enhanced server state management with proper async cleanup."""
    def __init__(self):
        self.active_tasks = weakref.WeakSet()
        self.chrome_instances = {}
        self.connection_lock = asyncio.Lock()
        self.cleanup_registered = False
        self.console_logs = []
        self.websocket_connections = {}
    
    async def add_task(self, task):
        """Add a task to be tracked for cleanup."""
        self.active_tasks.add(task)
    
    async def cleanup_all(self):
        """Clean up all active resources."""
        logger.info("Cleaning up server resources...")
        
        # Cancel all active tasks
        tasks_to_cancel = list(self.active_tasks)
        for task in tasks_to_cancel:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error during task cleanup: {e}")
        
        # Close WebSocket connections
        for ws in list(self.websocket_connections.values()):
            try:
                if hasattr(ws, 'close'):
                    await ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        logger.info(f"Cleaned up {len(tasks_to_cancel)} tasks and WebSocket connections")

# Global server state
server_state = ServerState()

async def run_background_task(coro, task_name: str = "unnamed"):
    """Run a coroutine as a background task with proper tracking."""
    try:
        task = asyncio.create_task(coro)
        task.set_name(task_name)
        await server_state.add_task(task)
        
        logger.info(f"Started background task: {task_name}")
        result = await task
        logger.info(f"Completed background task: {task_name}")
        return result
        
    except asyncio.CancelledError:
        logger.info(f"Background task cancelled: {task_name}")
        raise
    except Exception as e:
        logger.error(f"Background task failed: {task_name} - {e}")
        raise

# ============================================================================
# END NEW IMPROVEMENTS
# ============================================================================

# Configuration
SERVER_PORT = 8000
SERVER_HOST = "127.0.0.1"
SERVER_VERSION = "2.2.0"  # Enhanced AI-Assistant Edition

# Initialize FastMCP server
mcp = FastMCP("Cursor Development Assistant v2.1")

# Add health endpoint to fix 404 errors in logs
@mcp.custom_route("/health", methods=["GET"])
async def health_endpoint(request):
    """HTTP health endpoint for monitoring and load balancers"""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "server": "Cursor Development Assistant",
        "version": SERVER_VERSION,
        "timestamp": datetime.now().isoformat(),
        "transport": "http"
    })
SERVER_BUILD_TIME = datetime.now().isoformat()

# Chrome Debug Protocol configuration
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_HOST = "localhost"

# Global variables for Chrome connection management (kept for compatibility)
chrome_instances = {}
console_logs = []
console_log_listeners = {}
websocket_connections = {}  # Store persistent WebSocket connections
connection_lock = threading.Lock()

# Socket.IO client for orchestration
socketio_client = None
socketio_connected = False

# Resource cleanup tracking (enhanced by ServerState)
active_connections = set()
background_tasks = set()

# Multi-Agent Messaging System
# ===========================

import shutil
import re
from typing import Tuple

# Messaging system configuration
MESSAGING_ROOT = Path.cwd() / "messages"
AGENTS_DIR = MESSAGING_ROOT / "agents"
MESSAGES_DIR = MESSAGING_ROOT / "messages"
DELETED_DIR = MESSAGING_ROOT / "deleted"
SEQUENCE_FILE = MESSAGING_ROOT / "sequence.txt"

def ensure_messaging_directories():
    """Ensure all messaging directories exist."""
    for directory in [MESSAGING_ROOT, AGENTS_DIR, MESSAGES_DIR, DELETED_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Initialize sequence file if it doesn't exist
    if not SEQUENCE_FILE.exists():
        SEQUENCE_FILE.write_text("0")

def get_agent_name() -> str:
    """Get agent name from current repo directory."""
    return Path.cwd().name

def get_next_message_id() -> int:
    """Get next sequential message ID with proper locking."""
    ensure_messaging_directories()
    try:
        # Use file locking for thread safety
        try:
            import fcntl
            with open(SEQUENCE_FILE, 'r+') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    current_id = int(f.read().strip() or "0")
                    next_id = current_id + 1
                    f.seek(0)
                    f.write(str(next_id))
                    f.truncate()
                    return next_id
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except ImportError:
            # Fallback for systems without fcntl (Windows)
            try:
                current_id = int(SEQUENCE_FILE.read_text().strip() or "0")
                next_id = current_id + 1
                SEQUENCE_FILE.write_text(str(next_id))
                return next_id
            except Exception:
                SEQUENCE_FILE.write_text("1")
                return 1
    except (ValueError, FileNotFoundError):
        SEQUENCE_FILE.write_text("1")
        return 1

def register_agent() -> Dict[str, Any]:
    """Register current agent in the messaging system."""
    ensure_messaging_directories()
    
    agent_name = get_agent_name()
    agent_dir = AGENTS_DIR / agent_name
    agent_dir.mkdir(exist_ok=True)
    
    # Get repo information
    repo_path = str(Path.cwd().absolute())
    
    # Try to get GitHub remote URL
    github_url = None
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=5
        )
        if result.returncode == 0:
            github_url = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Create agent registration info
    registration_info = {
        "agent_name": agent_name,
        "repo_path": repo_path,
        "github_url": github_url,
        "registration_timestamp": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat()
    }
    
    # Save registration info
    agent_info_file = agent_dir / "info.json"
    with open(agent_info_file, 'w', encoding='utf-8') as f:
        json.dump(registration_info, f, indent=2)
    
    return registration_info

def get_agent_registration(agent_name: str) -> Optional[Dict[str, Any]]:
    """Get registration info for a specific agent."""
    agent_dir = AGENTS_DIR / agent_name
    agent_info_file = agent_dir / "info.json"
    
    if not agent_info_file.exists():
        return None
    
    try:
        with open(agent_info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def list_registered_agents() -> List[Dict[str, Any]]:
    """List all registered agents."""
    ensure_messaging_directories()
    agents = []
    
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            agent_info = get_agent_registration(agent_dir.name)
            if agent_info:
                agents.append(agent_info)
    
    return agents

def create_message(to: str, subject: str, message: str, reply_to: Optional[int] = None) -> Dict[str, Any]:
    """Create a new message."""
    ensure_messaging_directories()
    
    message_id = get_next_message_id()
    from_agent = get_agent_name()
    
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
    message_file = MESSAGES_DIR / f"{message_id}.json"
    with open(message_file, 'w', encoding='utf-8') as f:
        json.dump(message_data, f, indent=2)
    
    # Update sender's last active timestamp
    register_agent()
    
    return message_data

def get_messages(agent_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get messages for an agent with optional filtering."""
    ensure_messaging_directories()
    
    messages = []
    
    # Read all message files
    for message_file in MESSAGES_DIR.glob("*.json"):
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
            
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read message file {message_file}: {e}")
            continue
    
    # Sort by timestamp (newest first)
    messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return messages

def mark_message_read(message_id: int, agent_name: str) -> bool:
    """Mark a message as read."""
    message_file = MESSAGES_DIR / f"{message_id}.json"
    
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

def delete_message(message_id: int, agent_name: str) -> bool:
    """Delete a message (move to deleted folder). Only sender can delete."""
    message_file = MESSAGES_DIR / f"{message_id}.json"
    
    if not message_file.exists():
        return False
    
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            message_data = json.load(f)
        
        # Only allow the sender to delete
        if message_data.get("from") != agent_name:
            return False
        
        # Move to deleted folder
        deleted_file = DELETED_DIR / f"{message_id}.json"
        shutil.move(str(message_file), str(deleted_file))
        
        return True
        
    except (json.JSONDecodeError, IOError):
        return False

def read_agent_file(agent_name: str, file_path: str) -> Optional[str]:
    """Read a file from another agent's repo (if registered)."""
    agent_info = get_agent_registration(agent_name)
    if not agent_info:
        return None
    
    try:
        # Construct full path
        repo_path = Path(agent_info["repo_path"])
        full_path = repo_path / file_path
        
        # Security check: ensure path is within agent's repo
        if not str(full_path.resolve()).startswith(str(repo_path.resolve())):
            return None
        
        if full_path.exists() and full_path.is_file():
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
                
    except (IOError, OSError):
        pass
    
    return None

@mcp.tool()
def messages(operation: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Multi-agent messaging system for communication between MCP server instances.
    
    Operations:
    - send: Create new message (requires payload: {to, subject, message, reply_to?})
    - get: Get messages for current agent (optional payload for filtering)
    - list: List message summaries (optional payload for filtering)
    - delete: Delete message by ID (requires payload: {id})
    - reply: Reply to message (requires payload: {reply_to, message})
    - register: Register current agent in messaging system
    - agents: List all registered agents
    - read_file: Read file from another agent's repo (requires payload: {agent, file_path})
    
    Args:
        operation: The operation to perform
        payload: Operation-specific data
        
    Returns:
        Dict containing operation result and any relevant data
    """
    try:
        ensure_messaging_directories()
        current_agent = get_agent_name()
        
        if operation == "send":
            if not payload or not all(k in payload for k in ["to", "subject", "message"]):
                return {
                    "success": False,
                    "error": "send operation requires payload with 'to', 'subject', and 'message'"
                }
            
            # Check if target agent is registered
            target_agent = payload["to"]
            if not get_agent_registration(target_agent):
                return {
                    "success": False,
                    "error": f"Target agent '{target_agent}' is not registered"
                }
            
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
            
            # Mark first unread message as read if no specific filters
            if not filters and messages_list:
                unread_messages = [m for m in messages_list if not m.get("read", False)]
                if unread_messages:
                    mark_message_read(unread_messages[0]["id"], current_agent)
                    unread_messages[0]["read"] = True
            
            return {
                "success": True,
                "operation": "get",
                "agent": current_agent,
                "messages": messages_list
            }
        
        elif operation == "list":
            filters = payload or {}
            messages_list = get_messages(current_agent, filters)
            
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
            
            success = delete_message(payload["id"], current_agent)
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
            original_messages = get_messages(current_agent, {"id": payload["reply_to"]})
            if not original_messages:
                # Check if we sent the original message
                try:
                    message_file = MESSAGES_DIR / f"{payload['reply_to']}.json"
                    if message_file.exists():
                        with open(message_file, 'r', encoding='utf-8') as f:
                            original_message = json.load(f)
                        if original_message.get("from") == current_agent:
                            # We're replying to someone who messaged us
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
            
            message_data = create_message(
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
            registration_info = register_agent()
            return {
                "success": True,
                "operation": "register",
                "agent": registration_info
            }
        
        elif operation == "agents":
            agents_list = list_registered_agents()
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
            
            file_content = read_agent_file(payload["agent"], payload["file_path"])
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
        logger.error(f"Messages operation failed: {e}")
        return handle_error("messages", e, {"operation": operation, "payload": payload})

# Configuration
SERVER_PORT = 8000
SERVER_HOST = "127.0.0.1"
SERVER_VERSION = "2.0.1"
SERVER_BUILD_TIME = datetime.now().isoformat()

# Chrome Debug Protocol configuration
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_HOST = "localhost"

# Global variables for Chrome connection management
chrome_instances = {}
console_logs = []
console_log_listeners = {}
websocket_connections = {}  # Store persistent WebSocket connections
connection_lock = threading.Lock()

# Socket.IO client for orchestration
socketio_client = None
socketio_connected = False

# Resource cleanup tracking
active_connections = set()
background_tasks = set()

def cleanup_resources():
    """Clean up all resources on server shutdown."""
    logger.info("Cleaning up server resources...")
    
    # Close Socket.IO client connection
    global socketio_client, socketio_connected
    if socketio_client and socketio_connected:
        try:
            asyncio.create_task(socketio_client.disconnect())
            socketio_connected = False
            logger.info("Disconnected Socket.IO client")
        except Exception as e:
            logger.error(f"Error closing Socket.IO connection: {e}")
    
    # Close all WebSocket connections
    for ws in active_connections.copy():
        try:
            if hasattr(ws, 'close'):
                asyncio.create_task(ws.close())
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")
    
    # Cancel all background tasks
    for task in background_tasks.copy():
        try:
            task.cancel()
        except Exception as e:
            logger.error(f"Error canceling task: {e}")
    
    logger.info("Resource cleanup completed")

# Register cleanup handlers
atexit.register(cleanup_resources)
signal.signal(signal.SIGINT, lambda s, f: cleanup_resources())
signal.signal(signal.SIGTERM, lambda s, f: cleanup_resources())

def make_json_safe(obj):
    """Convert object to JSON-safe format with comprehensive Unicode handling."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        if isinstance(obj, str):
            try:
                # Handle Unicode encoding issues including surrogate pairs
                obj.encode('utf-8', 'strict')
                return obj
            except UnicodeEncodeError as e:
                logger.warning(f"Unicode encoding issue: {e}")
                # Handle surrogate pairs and invalid Unicode safely
                return obj.encode('utf-8', 'replace').decode('utf-8')
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    else:
        try:
            str_obj = str(obj)
            str_obj.encode('utf-8', 'strict')
            return str_obj
        except UnicodeEncodeError:
            return str(obj).encode('utf-8', 'replace').decode('utf-8')

def handle_error(operation: str, error: Exception, context: dict = None) -> dict:
    """Standard error response format for MCP tools."""
    error_response = {
        "success": False,
        "operation": operation,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        error_response["context"] = make_json_safe(context)
    
    # Log error for debugging
    logger.error(f"Error in {operation}: {error}", exc_info=True)
    
    return error_response

# Core File Operations


@mcp.tool()
def get_project_structure(directory: str = ".", max_depth: int = 3) -> Dict[str, Any]:
    """
    Get the structure of a project directory with security validation.
    
    Args:
        directory: Root directory to analyze
        max_depth: Maximum depth to traverse
        
    Returns:
        Dictionary representing the project structure
    """
    def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
        if current_depth >= max_depth:
            return {"truncated": True, "reason": "max_depth_reached"}
        
        result = {}
        try:
            items = list(path.iterdir())
            for item in sorted(items):
                # Skip hidden files and sensitive directories
                if item.name.startswith('.') and item.name not in ['.gitignore', '.env.example']:
                    continue
                
                if item.name in ['node_modules', '__pycache__', 'venv', '.git']:
                    result[item.name + "/"] = {"skipped": True, "reason": "common_ignore"}
                    continue
                    
                if item.is_dir():
                    result[item.name + "/"] = build_tree(item, current_depth + 1)
                else:
                    try:
                        stat = item.stat()
                        result[item.name] = {
                            "size": stat.st_size,
                            "type": "file",
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        }
                    except (OSError, PermissionError):
                        result[item.name] = {"error": "permission_denied"}
        except PermissionError:
            result["<permission_denied>"] = {"error": "insufficient_permissions"}
        except Exception as e:
            result["<error>"] = {"error": str(e)}
        
        return result
    
    try:
        dir_path = Path(directory).resolve()
        cwd = Path.cwd().resolve()
        
        if not str(dir_path).startswith(str(cwd)):
            return {"error": "Access denied: path outside working directory"}
        
        return {
            "structure": build_tree(dir_path),
            "metadata": {
                "directory": str(dir_path.relative_to(cwd)),
                "max_depth": max_depth,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_code(file_path: str) -> Dict[str, Any]:
    """
    Analyze a code file for comprehensive metrics and insights.
    
    Args:
        file_path: Path to the code file
        
    Returns:
        Dictionary with detailed code analysis results
    """
    try:
        file_path = Path(file_path).resolve()
        cwd = Path.cwd().resolve()
        
        if not str(file_path).startswith(str(cwd)):
            return {"error": "Access denied: path outside working directory"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        ext = file_path.suffix.lower()
        
        analysis = {
            "file_path": str(file_path.relative_to(cwd)),
            "file_size": len(content.encode('utf-8')),
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": 0,
            "function_count": 0,
            "class_count": 0,
            "import_count": 0,
            "complexity_indicators": {
                "nested_blocks": 0,
                "long_lines": 0,  # Lines > 100 chars
                "todos": 0
            }
        }
        
        # Language-specific analysis
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Count long lines
            if len(line) > 100:
                analysis["complexity_indicators"]["long_lines"] += 1
            
            # Count TODOs
            if any(todo in stripped.upper() for todo in ['TODO', 'FIXME', 'XXX', 'HACK']):
                analysis["complexity_indicators"]["todos"] += 1
            
            # Language-specific patterns
            if ext == '.py':
                if stripped.startswith('#'):
                    analysis["comment_lines"] += 1
                elif stripped.startswith('def '):
                    analysis["function_count"] += 1
                elif stripped.startswith('class '):
                    analysis["class_count"] += 1
                elif stripped.startswith(('import ', 'from ')):
                    analysis["import_count"] += 1
                    
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                if stripped.startswith('//') or stripped.startswith('/*'):
                    analysis["comment_lines"] += 1
                elif 'function ' in stripped or '=>' in stripped:
                    analysis["function_count"] += 1
                elif 'class ' in stripped:
                    analysis["class_count"] += 1
                elif stripped.startswith(('import ', 'const ', 'require(')):
                    analysis["import_count"] += 1
        
        # Calculate ratios
        if analysis["total_lines"] > 0:
            analysis["comment_ratio"] = analysis["comment_lines"] / analysis["total_lines"]
            analysis["code_density"] = analysis["non_empty_lines"] / analysis["total_lines"]
        
        analysis["timestamp"] = datetime.now().isoformat()
        return analysis
        
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}



# System Information
@mcp.tool()
def get_system_info(include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Get system and environment information with privacy controls.
    
    Args:
        include_sensitive: Whether to include sensitive system information
        
    Returns:
        System information dictionary
    """
    try:
        import platform
        import psutil
        
        info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable": sys.executable
            },
            "working_directory": str(Path.cwd()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add system resource info if psutil is available
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info["resources"] = {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        except ImportError:
            info["resources"] = {"note": "psutil not available for detailed resource info"}
        
        if include_sensitive:
            info["environment"] = {
                k: v for k, v in os.environ.items() 
                if not any(sensitive in k.upper() for sensitive in ['PASSWORD', 'TOKEN', 'KEY', 'SECRET'])
            }
        
        return info
        
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@mcp.tool()
def server_info() -> Dict[str, Any]:
    """Get comprehensive MCP server information and status."""
    try:
        # Get tools from the MCP server
        tools_list = []
        try:
            # Since get_tools() is async, we'll use a different approach
            # Count tools by looking at all function objects with 'fn' attribute
            import inspect
            tools_list = [name for name, obj in globals().items() 
                         if hasattr(obj, 'fn') and hasattr(obj, 'name')]
        except Exception as e:
            logger.warning(f"Could not get tools list: {e}")
        
        return {
            "server_name": "Cursor Development Assistant",
            "version": SERVER_VERSION,
            "build_time": SERVER_BUILD_TIME,
            "description": "Consolidated MCP server with Chrome Debug Protocol integration",
            "transport": "HTTP",
            "host": SERVER_HOST,
            "port": SERVER_PORT,
            "tools": {
                "count": len(tools_list),
                "available": sorted(tools_list)
            },
            "chrome_debug": {
                "enabled": True,
                "port": CHROME_DEBUG_PORT,
                "active_instances": len(chrome_instances),
                "active_listeners": len(console_log_listeners),
                "total_console_logs": len(console_logs)
            },
            "features": [
                "File operations with security validation",
                "Enhanced code analysis",
                "Git integration (read-only)",
                "SQLite database operations",
                "Chrome Debug Protocol integration",
                "Real-time console monitoring",
                "JavaScript execution in browser",
                "Breakpoint management",
                "Unicode-safe logging"
            ],
            "status": "operational",
            "current_time": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@mcp.tool()
def health() -> Dict[str, Any]:
    """
    Simple health endpoint for monitoring and testing.
    
    Returns basic server health status and uptime information.
    Useful for load balancers, monitoring systems, and end-to-end tests.
    
    Returns:
        Dict containing health status and basic metrics
    """
    try:
        # Check if Chrome Debug Protocol is available
        chrome_available = False
        try:
            response = requests.get(f"http://{CHROME_DEBUG_HOST}:{CHROME_DEBUG_PORT}/json", timeout=2)
            chrome_available = response.status_code == 200
        except:
            pass
        
        return {
            "status": "healthy",
            "server": "Cursor Development Assistant",
            "version": SERVER_VERSION,
            "timestamp": datetime.now().isoformat(),
            "uptime_info": {
                "build_time": SERVER_BUILD_TIME,
                "current_time": datetime.now().isoformat()
            },
            "services": {
                "mcp_server": "operational",
                "chrome_debug": "available" if chrome_available else "inactive",
                "socketio_client": "connected" if socketio_connected else "disconnected"
            },
            "metrics": {
                "active_chrome_instances": len(chrome_instances),
                "console_log_listeners": len(console_log_listeners),
                "total_console_logs": len(console_logs),
                "active_connections": len(active_connections)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@asynccontextmanager
async def websocket_connection(ws_url: str):
    """Context manager for safe WebSocket connections."""
    ws = None
    try:
        ws = await websockets.connect(ws_url)
        active_connections.add(ws)
        yield ws
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        raise
    finally:
        if ws:
            active_connections.discard(ws)
            await ws.close()

async def send_chrome_command_async(ws_url: str, command: str, params: Dict = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Send command to Chrome Debug Protocol with proper async handling.
    
    Args:
        ws_url: WebSocket URL for the Chrome tab
        command: Chrome DevTools Protocol command
        params: Command parameters
        timeout: Timeout in seconds
        
    Returns:
        Command response or error information
    """
    # CRITICAL: Chrome Debug Protocol requires INTEGER request IDs, not strings
    # String IDs cause error: "Message must have integer 'id' property"
    request_id = int(time.time() * 1000000) % 1000000  # Generate unique integer ID from timestamp
    message = {
        "id": request_id,
        "method": command,
        "params": params or {}
    }
    
    try:
        async with websocket_connection(ws_url) as websocket:
            # Send command
            await websocket.send(json.dumps(message))
            logger.info(f"Sent Chrome command: {command} with ID: {request_id}")
            
            # Wait for response with timeout
            start_time = time.time()
            messages_received = 0
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    messages_received += 1
                    
                    # Skip events, only process our response
                    if data.get("id") == request_id:
                        logger.info(f"Received response for command {command} after {messages_received} messages")
                        return {
                            "success": True,
                            "command": command,
                            "request_id": request_id,
                            "result": data.get("result", {}),
                            "error": data.get("error"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        # Log events for debugging
                        if "method" in data:
                            logger.info(f"Received event #{messages_received}: {data['method']}")
                        else:
                            logger.info(f"Received unexpected message #{messages_received}: {data}")
                        
                except asyncio.TimeoutError:
                    logger.info(f"1-second recv timeout, {messages_received} messages so far, continuing...")
                    continue
            
            return {
                "success": False,
                "error": f"Timeout waiting for response to {command}",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in Chrome command {command}: {e}")
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def connect_to_chrome(port: int = 9222, host: str = "localhost") -> Dict[str, Any]:
    """
    Connect to Chrome Debug Protocol with enhanced error handling.
    
    Args:
        port: Chrome debug port
        host: Chrome debug host
        
    Returns:
        Connection information and available tabs
    """
    try:
        connection_id = f"{host}:{port}"
        
        # Test connection
        response = requests.get(f"http://{host}:{port}/json", timeout=5)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to connect to Chrome debug port {port}",
                "suggestion": "Ensure Chrome is running with --remote-debugging-port=9222"
            }
        
        tabs_data = response.json()
        
        # Store connection info
        with connection_lock:
            chrome_instances[connection_id] = {
                "host": host,
                "port": port,
                "connected_at": datetime.now().isoformat(),
                "tabs": len(tabs_data)
            }
        
        logger.info(f"Connected to Chrome at {connection_id} with {len(tabs_data)} tabs")
        
        return {
            "success": True,
            "connection_id": connection_id,
            "host": host,
            "port": port,
            "tabs_available": len(tabs_data),
            "tabs": [
                {
                    "id": tab.get("id"),
                    "title": tab.get("title", "")[:100],  # Limit title length
                    "url": tab.get("url", "")[:200],      # Limit URL length
                    "type": tab.get("type"),
                    "webSocketDebuggerUrl": tab.get("webSocketDebuggerUrl")
                }
                for tab in tabs_data if tab.get("type") in ["page", "background_page"]
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Connection refused to {host}:{port}",
            "suggestion": "Launch Chrome with: ./launch-chrome-debug.sh or chrome --remote-debugging-port=9222"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Timeout connecting to {host}:{port}",
            "suggestion": "Check if Chrome debug port is responsive"
        }
    except Exception as e:
        logger.error(f"Unexpected error connecting to Chrome: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_chrome_tabs(connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Get available Chrome tabs with enhanced filtering and information.
    
    Args:
        connection_id: Chrome connection identifier
        
    Returns:
        List of available tabs with detailed information
    """
    try:
        if connection_id not in chrome_instances:
            return {
                "success": False,
                "error": "Not connected to Chrome. Use connect_to_chrome first.",
                "available_connections": list(chrome_instances.keys())
            }
        
        host, port = connection_id.split(":")
        response = requests.get(f"http://{host}:{port}/json", timeout=5)
        
        if response.status_code != 200:
            return {"success": False, "error": f"Failed to get tabs from {connection_id}"}
        
        tabs_data = response.json()
        
        # Filter and enhance tab information
        filtered_tabs = []
        for tab in tabs_data:
            if tab.get("type") in ["page", "background_page"] and tab.get("webSocketDebuggerUrl"):
                tab_info = {
                    "id": tab.get("id"),
                    "title": make_json_safe(tab.get("title", "")[:100]),
                    "url": tab.get("url", "")[:200],
                    "type": tab.get("type"),
                    "webSocketDebuggerUrl": tab.get("webSocketDebuggerUrl"),
                    "favicon": tab.get("faviconUrl", ""),
                    "description": tab.get("description", "")[:100]
                }
                
                # Add extension-specific information
                if "extension" in tab.get("url", "").lower():
                    tab_info["is_extension"] = True
                    tab_info["extension_type"] = "popup" if "popup" in tab.get("url", "") else "background"
                
                filtered_tabs.append(tab_info)
        
        return {
            "success": True,
            "connection_id": connection_id,
            "total_tabs": len(tabs_data),
            "debuggable_tabs": len(filtered_tabs),
            "tabs": filtered_tabs,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Chrome tabs: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def launch_chrome_debug() -> Dict[str, Any]:
    """
    Launch Chrome with debugging enabled and proper configuration.
    
    Returns:
        Launch status and connection information
    """
    try:
        # Use the python launch script
        script_path = Path("./chrome_debug_launcher.py")
        
        if script_path.exists():
            logger.info("Using existing launch script")
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Wait a moment for Chrome to start
                time.sleep(2)
                
                # Test connection
                connection_result = connect_to_chrome()
                
                return {
                    "success": True,
                    "method": "launch_script",
                    "script_output": result.stdout,
                    "connection_test": connection_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Launch script failed: {result.stderr}")
        
                return {
                    "success": False,
                    "error": "Could not launch Chrome with debugging enabled",
                    "suggestions": [
                        "Install Google Chrome",
                        "Run: ./launch-chrome-debug.sh",
                        "Manual: chrome --remote-debugging-port=9222 --remote-allow-origins=*"
                    ]
                }
        
    except Exception as e:
        logger.error(f"Error launching Chrome debug: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def execute_javascript(code: str, tab_id: str, connection_id: str = "localhost:9222") -> Dict[str, Any]:
    """
    Execute JavaScript in Chrome tab with proper async handling and error reporting.
    
    Args:
        code: JavaScript code to execute
        tab_id: Chrome tab ID
        connection_id: Chrome connection identifier
        
    Returns:
        Execution result with comprehensive error handling
    """
    def run_async_execution():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def execute():
                # Get WebSocket URL for the tab
                host, port = connection_id.split(":")
                response = requests.get(f"http://{host}:{port}/json", timeout=5)
                
                if response.status_code != 200:
                    return {"success": False, "error": "Failed to get tab information"}
                
                tabs = response.json()
                target_tab = None
                
                for tab in tabs:
                    if tab.get("id") == tab_id:
                        target_tab = tab
                        break
                
                if not target_tab:
                    return {"success": False, "error": f"Tab {tab_id} not found"}
                
                ws_url = target_tab.get("webSocketDebuggerUrl")
                if not ws_url:
                    return {"success": False, "error": f"Tab {tab_id} not debuggable"}
                
                # Enable Runtime domain
                enable_result = await send_chrome_command_async(ws_url, "Runtime.enable")
                if not enable_result.get("success"):
                    return {"success": False, "error": "Failed to enable Runtime domain"}
                
                # Execute JavaScript
                exec_result = await send_chrome_command_async(
                    ws_url,
                    "Runtime.evaluate",
                    {
                        "expression": code,
                        "returnByValue": True,
                        "generatePreview": True
                    }
                )
                
                if not exec_result.get("success"):
                    return exec_result
                
                result = exec_result.get("result", {})
                
                # Process execution result
                if result.get("exceptionDetails"):
                    exception = result["exceptionDetails"]
                    return {
                        "success": False,
                        "error": "JavaScript execution error",
                        "exception": make_json_safe(exception),
                        "line_number": exception.get("lineNumber"),
                        "column_number": exception.get("columnNumber"),
                        "timestamp": datetime.now().isoformat()
                    }
                
                execution_result = result.get("result", {})
                return {
                    "success": True,
                    "value": make_json_safe(execution_result.get("value")),
                    "type": execution_result.get("type"),
                    "description": execution_result.get("description"),
                    "code_executed": code,
                    "tab_id": tab_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            return loop.run_until_complete(execute())
            
        except Exception as e:
            logger.error(f"Error in JavaScript execution: {e}")
            return {"success": False, "error": str(e)}
        finally:
            loop.close()
    
    try:
        if connection_id not in chrome_instances:
            return {"success": False, "error": "Not connected to Chrome. Use connect_to_chrome first."}
        
        # Run in separate thread to avoid blocking
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async_execution)
            result = future.result(timeout=30)  # 30 second timeout
            
        return make_json_safe(result)
        
    except concurrent.futures.TimeoutError:
        return {"success": False, "error": "JavaScript execution timed out"}
    except Exception as e:
        logger.error(f"Unexpected error in JavaScript execution: {e}")
        return {"success": False, "error": str(e)}






# =================================================================
# ORCHESTRATION TOOLS - Multi-LLM Coordination
# =================================================================

async def initialize_socketio_client():
    """Initialize Socket.IO client connection."""
    global socketio_client, socketio_connected
    
    if socketio_client is None:
        socketio_client = socketio.AsyncClient()
        
        @socketio_client.event
        async def connect():
            global socketio_connected
            socketio_connected = True
            logger.info("✅ Connected to Socket.IO server for orchestration")
            
        @socketio_client.event
        async def disconnect():
            global socketio_connected
            socketio_connected = False
            logger.info("❌ Disconnected from Socket.IO server")
            
        @socketio_client.event
        async def orchestration_response(data):
            logger.info(f"📬 Received orchestration response: {data}")
    
    try:
        if not socketio_connected:
            await socketio_client.connect('http://localhost:3001')
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Socket.IO server: {e}")
        return False

@mcp.tool()
def send_orchestration_command(
    command_type: str, 
    targets: List[str], 
    prompt: str, 
    options: Dict = None
) -> Dict[str, Any]:
    """
    Send orchestration command to extension via Socket.IO for multi-LLM coordination.
    
    This tool enables Claude Desktop to orchestrate multiple AI services (ChatGPT, Claude.ai, etc.)
    through the Chrome extension, collecting and aggregating their responses.
    
    Args:
        command_type: Type of command ('code_generation', 'analysis', 'chat')
        targets: List of AI services to target ['chatgpt', 'claude', 'perplexity']
        prompt: The prompt to send to all target AI services
        options: Optional parameters (timeout, priority, etc.)
        
    Returns:
        Dictionary with command dispatch status and tracking ID
        
    Example:
        send_orchestration_command(
            command_type="code_generation",
            targets=["chatgpt", "claude"],
            prompt="Build a React chat component",
            options={"timeout": 120}
        )
    """
    async def async_send_command():
        try:
            # Initialize Socket.IO client if needed
            connection_success = await initialize_socketio_client()
            if not connection_success:
                return {
                    "success": False, 
                    "error": "Failed to connect to Socket.IO server",
                    "details": "Ensure socketio_server.js is running on localhost:3001"
                }
            
            # Create orchestration command
            command_id = str(uuid.uuid4())
            command = {
                "id": command_id,
                "type": command_type,
                "prompt": prompt,
                "targets": targets,
                "timeout": options.get("timeout", 120) if options else 120,
                "priority": options.get("priority", "normal") if options else "normal",
                "timestamp": datetime.now().isoformat(),
                "source": "claude_desktop_mcp"
            }
            
            # Send command via Socket.IO
            await socketio_client.emit('orchestration_command', command)
            
            logger.info(f"🚀 Sent orchestration command {command_id} to {len(targets)} targets")
            
            return {
                "success": True,
                "command_id": command_id,
                "targets": targets,
                "message": f"Orchestration command sent to {len(targets)} AI services",
                "tracking": {
                    "command_type": command_type,
                    "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "targets": targets,
                    "timeout": command.get("timeout"),
                    "timestamp": command.get("timestamp")
                }
            }
            
        except Exception as e:
            logger.error(f"Error sending orchestration command: {e}")
            return {
                "success": False,
                "error": f"Failed to send orchestration command: {str(e)}",
                "error_type": type(e).__name__
            }
    
    # Run async function in event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_send_command())
            return make_json_safe(result)
        finally:
            loop.close()
    except Exception as e:
        return {
            "success": False,
            "error": f"Event loop error: {str(e)}",
            "details": "Failed to execute async Socket.IO operation"
        }

# =================================================================
# NATIVE BROWSER AUTOMATION TOOLS
# =================================================================

@mcp.tool()
def inject_prompt_native(
    prompt: str,
    browser: str = "Chrome",
    use_tab_navigation: bool = True,
    use_clipboard: bool = True,
    typing_delay: float = 0.05,
    delay_between_steps: float = 1.0
) -> Dict[str, Any]:
    """
    Inject prompt into any web browser AI interface using native keyboard automation.
    
    This bypasses JavaScript validation and appears as genuine user input to the browser.
    Works with Gemini, ChatGPT, Claude.ai, or any web-based AI interface.
    
    Args:
        prompt: Text prompt to inject
        browser: Browser name to focus ('Chrome', 'Safari', 'Firefox', 'Edge')
        use_tab_navigation: Whether to use Tab key to navigate to input field
        use_clipboard: If True, use copy/paste instead of typing (much faster)
        typing_delay: Delay between keystrokes in seconds (0 for instant, 0.05 for human-like)
        delay_between_steps: Delay between major automation steps
        
    Returns:
        Dictionary with injection status and detailed step results
    """
    try:
        # Import the native injector
        import sys
        import os
        
        # Add current directory to path to import our injector
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from gemini_native_injector import GeminiNativeInjector
        
        # Create injector instance
        injector = GeminiNativeInjector()
        
        # Execute the injection
        result = injector.inject_gemini_prompt(
            prompt=prompt,
            browser=browser,
            use_tab_navigation=use_tab_navigation,
            use_clipboard=use_clipboard,
            typing_delay=typing_delay,
            delay_between_steps=delay_between_steps
        )
        
        # Make the result JSON-safe
        return make_json_safe(result)
        
    except ImportError as e:
        return {
            "success": False,
            "error": f"Failed to import native injector: {str(e)}",
            "details": "Ensure gemini_native_injector.py is in the same directory"
        }
    except Exception as e:
        logger.error(f"Native injection failed: {e}")
        return {
            "success": False,
            "error": f"Native injection failed: {str(e)}",
            "error_type": type(e).__name__
        }

@mcp.tool()
def focus_and_type_native(
    text: str,
    app_name: str = "Chrome",
    typing_delay: float = 0.05
) -> Dict[str, Any]:
    """
    Focus an application and type text using native automation.
    
    Useful for injecting text into any application, not just browsers.
    
    Args:
        text: Text to type
        app_name: Application name to focus
        typing_delay: Delay between keystrokes (0 for instant)
        
    Returns:
        Dictionary with automation status
    """
    try:
        from gemini_native_injector import GeminiNativeInjector
        
        injector = GeminiNativeInjector()
        
        result = {
            'success': False,
            'steps': [],
            'error': None,
            'app_name': app_name,
            'text_length': len(text)
        }
        
        # Focus the application
        if app_name.lower() in ['chrome', 'safari', 'firefox', 'edge']:
            success, message = injector.focus_browser(app_name)
        else:
            # For non-browser apps, try generic focus (this would need platform-specific implementation)
            success, message = False, f"Generic app focus not implemented for {app_name}"
        
        result['steps'].append({'step': 'focus_app', 'success': success, 'message': message})
        
        if not success:
            result['error'] = f"Failed to focus {app_name}: {message}"
            return make_json_safe(result)
        
        # Type the text
        time.sleep(0.5)  # Small delay after focusing
        success, message = injector.type_text(text, typing_delay)
        result['steps'].append({'step': 'type_text', 'success': success, 'message': message})
        
        if success:
            result['success'] = True
        else:
            result['error'] = f"Failed to type text: {message}"
        
        return make_json_safe(result)
        
    except Exception as e:
        logger.error(f"Focus and type failed: {e}")
        return {
            "success": False,
            "error": f"Focus and type failed: {str(e)}",
            "error_type": type(e).__name__
        }

# Add the remaining Chrome debugging functions here...
# (console monitoring, breakpoints, etc.)

# ============================================================================
# CLEAN NOTIFICATION SYSTEM FOR MULTI-AGENT COORDINATION
# ============================================================================

# Notification system configuration
NOTIFICATIONS_ROOT = MESSAGING_ROOT / "notifications"
NOTIFICATIONS_DIR = NOTIFICATIONS_ROOT / "pending"
CANCEL_FLAGS_DIR = NOTIFICATIONS_ROOT / "cancel_flags"

def ensure_notification_directories():
    """Ensure all notification directories exist."""
    for directory in [NOTIFICATIONS_ROOT, NOTIFICATIONS_DIR, CANCEL_FLAGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def create_notification(target_agent: str, message: str, sender: str = None) -> Dict[str, Any]:
    """Create a notification for target agent."""
    ensure_notification_directories()
    
    if sender is None:
        sender = get_agent_name()
    
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
    notification_file = NOTIFICATIONS_DIR / f"{target_agent}_{notification_id}.json"
    temp_file = notification_file.with_suffix('.tmp')
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(notification_data, f, indent=2)
    
    temp_file.rename(notification_file)
    
    # Immediately wake up waiting agent (event-driven)
    asyncio.create_task(comm_hub.notify_agent(target_agent, "notification"))
    
    logger.info(f"Created notification {notification_id} for {target_agent} from {sender}")
    return notification_data

def get_pending_notifications(agent_name: str) -> List[Dict[str, Any]]:
    """Get all pending notifications for an agent."""
    ensure_notification_directories()
    
    notifications = []
    pattern = f"{agent_name}_*.json"
    
    for notification_file in NOTIFICATIONS_DIR.glob(pattern):
        try:
            with open(notification_file, 'r', encoding='utf-8') as f:
                notification_data = json.load(f)
            notifications.append(notification_data)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read notification file {notification_file}: {e}")
            continue
    
    # Sort by timestamp (oldest first)
    notifications.sort(key=lambda x: x.get("created_at", 0))
    return notifications

def delete_notifications(agent_name: str, notification_ids: List[str] = None) -> int:
    """Delete delivered notifications."""
    ensure_notification_directories()
    
    deleted_count = 0
    pattern = f"{agent_name}_*.json"
    
    for notification_file in NOTIFICATIONS_DIR.glob(pattern):
        try:
            if notification_ids is None:
                # Delete all notifications for agent
                notification_file.unlink()
                deleted_count += 1
            else:
                # Delete specific notifications
                with open(notification_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get("id") in notification_ids:
                    notification_file.unlink()
                    deleted_count += 1
        except Exception as e:
            logger.warning(f"Failed to delete notification {notification_file}: {e}")
    
    logger.info(f"Deleted {deleted_count} notifications for {agent_name}")
    return deleted_count

def set_cancel_flag(agent_name: str) -> bool:
    """Set cancel flag to interrupt waiting agent."""
    ensure_notification_directories()
    
    cancel_file = CANCEL_FLAGS_DIR / f"{agent_name}.cancel"
    try:
        cancel_file.write_text(datetime.now().isoformat())
        logger.info(f"Set cancel flag for {agent_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to set cancel flag for {agent_name}: {e}")
        return False

def check_cancel_flag(agent_name: str) -> bool:
    """Check if agent has a cancel flag set."""
    ensure_notification_directories()
    
    cancel_file = CANCEL_FLAGS_DIR / f"{agent_name}.cancel"
    if cancel_file.exists():
        try:
            cancel_file.unlink()  # Remove flag after checking
            logger.info(f"Cancel flag found and cleared for {agent_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to clear cancel flag for {agent_name}: {e}")
    return False

@mcp.tool()
async def notify(operation: str, target_agent: str = None, message: str = None, sender: str = None, agent_name: str = None) -> Dict[str, Any]:
    """
    Clean notification system for multi-agent coordination.
    
    Operations:
    - notify: Send notification to target agent
      Args: target_agent (str), message (str), [sender (str)]
    - wait: Wait for incoming notifications (returns all pending)
      Args: agent_name (str) - the agent waiting for notifications
    - cancel_wait: Interrupt a waiting agent  
      Args: target_agent (str)
    - check: Check for pending notifications without waiting
      Args: agent_name (str) - the agent checking for notifications
    
    Args:
        operation: The operation to perform
        target_agent: Target agent name (required for notify and cancel_wait)
        message: Message text (required for notify)
        sender: Sender name (optional, defaults to current agent)
        agent_name: Agent name for wait/check operations (required for wait/check)
        
    Returns:
        Dict containing operation result
    """
    try:
        # For backward compatibility, fall back to directory-based name if not provided
        current_agent = agent_name if agent_name else get_agent_name()
        
        if operation == "notify":
            if not target_agent or not message:
                return {
                    "success": False,
                    "error": "notify operation requires 'target_agent' and 'message'"
                }
            
            notification = create_notification(target_agent, message, sender)
            
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
            result = await comm_hub.wait_for_communication(current_agent, include_messages=False)
            return result
        
        elif operation == "cancel_wait":
            if not target_agent:
                return {
                    "success": False,
                    "error": "cancel_wait operation requires 'target_agent'"
                }
            
            success = set_cancel_flag(target_agent)
            
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
            
            notifications = get_pending_notifications(current_agent)
            
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
        return handle_error("notify", e, {"operation": operation, "target_agent": target_agent, "message": message, "agent_name": agent_name})

# ============================================================================
# END NOTIFICATION SYSTEM
# ============================================================================

# ============================================================================
# EVENT-DRIVEN COMMUNICATION HUB
# ============================================================================

class CommunicationHub:
    """Event-driven communication hub for immediate multi-agent coordination."""
    
    def __init__(self):
        self.waiting_agents = {}  # agent_name -> asyncio.Event
        self.agent_timeouts = {}  # agent_name -> timeout_handle
        self._lock = asyncio.Lock()
    
    async def wait_for_communication(self, agent_name: str, include_messages: bool = False, timeout: float = None) -> Dict[str, Any]:
        """Wait for any communication (notifications and optionally messages) for an agent."""
        start_time = time.time()
        
        # Check for existing communications first
        existing_comms = await self._get_existing_communications(agent_name, include_messages)
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
            comms = await self._get_existing_communications(agent_name, include_messages)
            
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
    
    async def _get_existing_communications(self, agent_name: str, include_messages: bool) -> Dict[str, Any]:
        """Get existing notifications and optionally messages for an agent."""
        notifications = get_pending_notifications(agent_name)
        messages = []
        
        if include_messages:
            messages = get_messages(agent_name, {"unread_only": True})
        
        # Clean up delivered communications
        if notifications:
            delivered_ids = [n["id"] for n in notifications]
            delete_notifications(agent_name, delivered_ids)
        
        if messages:
            for msg in messages:
                mark_message_read(msg["id"], agent_name)
        
        return {
            "notifications": notifications,
            "messages": messages,
            "total_count": len(notifications) + len(messages),
            "has_communications": len(notifications) > 0 or len(messages) > 0
        }
    
    def get_waiting_agents(self) -> List[str]:
        """Get list of currently waiting agents."""
        return list(self.waiting_agents.keys())

# Global communication hub instance
comm_hub = CommunicationHub()

# ============================================================================
# END EVENT-DRIVEN COMMUNICATION HUB
# ============================================================================

# ============================================================================
# ENHANCED NOTIFICATION SYSTEM WITH EVENT-DRIVEN SUPPORT
# ============================================================================

# ============================================================================
# ENHANCED ERROR LOGGING AND FILE OPERATIONS FOR AI ASSISTANTS
# ============================================================================

# Global error log storage with agent tracking
agent_error_logs = {}  # agent_name -> list of error entries
error_log_lock = threading.Lock()

def log_agent_error(operation: str, error: Exception, context: dict = None, agent_name: str = None) -> str:
    """
    Log error with agent tracking and return error ID for retrieval.
    
    Args:
        operation: Name of the operation that failed
        error: The exception that occurred
        context: Additional context information
        agent_name: Name of the agent (auto-detected if None)
        
    Returns:
        Error ID for later retrieval
    """
    if agent_name is None:
        agent_name = get_agent_name()
    
    error_id = f"{int(time.time() * 1000000)}_{uuid.uuid4().hex[:8]}"
    
    error_entry = {
        "error_id": error_id,
        "operation": operation,
        "error": str(error),
        "error_type": type(error).__name__,
        "traceback": traceback.format_exc(),
        "context": make_json_safe(context) if context else None,
        "agent_name": agent_name,
        "timestamp": datetime.now().isoformat(),
        "unix_timestamp": time.time()
    }
    
    # Store error with thread safety
    with error_log_lock:
        if agent_name not in agent_error_logs:
            agent_error_logs[agent_name] = []
        
        agent_error_logs[agent_name].append(error_entry)
        
        # Keep only last 50 errors per agent to prevent memory bloat
        if len(agent_error_logs[agent_name]) > 50:
            agent_error_logs[agent_name] = agent_error_logs[agent_name][-50:]
    
    # Log to file as well
    logger.error(f"Error {error_id} in {operation} for agent {agent_name}: {error}", exc_info=True)
    
    return error_id

def enhanced_handle_error(operation: str, error: Exception, context: dict = None, agent_name: str = None) -> dict:
    """Enhanced error response with agent tracking and detailed information."""
    error_id = log_agent_error(operation, error, context, agent_name)
    
    error_response = {
        "success": False,
        "operation": operation,
        "error": str(error),
        "error_type": type(error).__name__,
        "error_id": error_id,
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name or get_agent_name(),
        "suggestion": get_error_suggestion(error, operation)
    }
    
    if context:
        error_response["context"] = make_json_safe(context)
    
    return error_response

def get_error_suggestion(error: Exception, operation: str) -> str:
    """Get helpful suggestion based on error type and operation."""
    error_type = type(error).__name__
    
    suggestions = {
        "FileNotFoundError": f"File not found. Check if the path exists or create the directory first.",
        "PermissionError": f"Permission denied. Ensure you have write access to the target location.",
        "UnicodeDecodeError": f"File encoding issue. The file may be binary or use a different encoding.",
        "JSONDecodeError": f"Invalid JSON format. Check the JSON syntax.",
        "ConnectionError": f"Network connection failed. Check if the service is running.",
        "TimeoutError": f"Operation timed out. The service may be overloaded.",
        "ValueError": f"Invalid parameter value. Check the input parameters.",
        "TypeError": f"Incorrect data type. Check the parameter types.",
        "ImportError": f"Missing dependency. Install required packages.",
        "OSError": f"Operating system error. Check system resources and permissions."
    }
    
    return suggestions.get(error_type, f"Unexpected {error_type} in {operation}. Check the error details above.")

@mcp.tool()
def get_last_errors(agent_name: str = None, limit: int = 10, operation_filter: str = None) -> Dict[str, Any]:
    """
    Get recent errors for an agent with filtering options.
    
    Args:
        agent_name: Agent name (defaults to current agent)
        limit: Maximum number of errors to return
        operation_filter: Filter by operation name (optional)
        
    Returns:
        Dictionary with error list and metadata
    """
    try:
        if agent_name is None:
            agent_name = get_agent_name()
        
        with error_log_lock:
            agent_errors = agent_error_logs.get(agent_name, [])
        
        # Apply operation filter if specified
        if operation_filter:
            agent_errors = [e for e in agent_errors if operation_filter.lower() in e["operation"].lower()]
        
        # Sort by timestamp (newest first) and limit
        sorted_errors = sorted(agent_errors, key=lambda x: x["unix_timestamp"], reverse=True)
        limited_errors = sorted_errors[:limit]
        
        return {
            "success": True,
            "agent_name": agent_name,
            "errors": limited_errors,
            "total_errors": len(agent_errors),
            "filtered_count": len(limited_errors),
            "operation_filter": operation_filter,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return handle_error("get_last_errors", e)



# Enhanced File Operations for AI Assistants
@mcp.tool()
def smart_write_file(
    file_path: str, 
    content: str, 
    mode: str = "overwrite",
    backup: bool = True,
    create_dirs: bool = True,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Advanced file writing with multiple modes and comprehensive error handling.
    
    Args:
        file_path: Path to the file to write 
        content: Content to write
        mode: Write mode ('overwrite', 'append', 'insert_at_line', 'replace_section')
        backup: Create backup before writing
        create_dirs: Create parent directories if they don't exist
        encoding: File encoding (default: utf-8)
        
    Returns:
        Detailed write result with metadata
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        file_path = Path(file_path).resolve()
        cwd = Path.cwd().resolve()
        
        # Security validation
        if not str(file_path).startswith(str(cwd)):
            error = SecurityError("Access denied: path outside working directory")
            return enhanced_handle_error("smart_write_file", error, 
                                       {"file_path": str(file_path), "mode": mode}, agent_name)
        
        original_content = ""
        file_existed = file_path.exists()
        original_size = 0
        
        # Read original content if file exists
        if file_existed:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    original_content = f.read()
                    original_size = len(original_content.encode(encoding))
            except UnicodeDecodeError:
                # Try different encodings
                for alt_encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=alt_encoding) as f:
                            original_content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise UnicodeDecodeError(f"Could not decode file with any supported encoding")
        
        # Create backup if requested and file exists
        backup_path = None
        if backup and file_existed and original_content:
            backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{int(time.time())}')
            with open(backup_path, 'w', encoding=encoding) as f:
                f.write(original_content)
            logger.info(f"Created backup: {backup_path}")
        
        # Create parent directories if requested
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle different write modes
        final_content = content
        
        if mode == "append":
            final_content = original_content + content
        elif mode == "prepend":
            final_content = content + original_content
        elif mode == "overwrite":
            final_content = content
        else:
            # Default to overwrite for unknown modes
            logger.warning(f"Unknown write mode '{mode}', defaulting to overwrite")
            final_content = content
        
        # Write the file
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(final_content)
        
        new_size = len(final_content.encode(encoding))
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "smart_write_file",
            "file_path": str(file_path.relative_to(cwd)),
            "mode": mode,
            "file_existed": file_existed,
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path.relative_to(cwd)) if backup_path else None,
            "original_size": original_size,
            "new_size": new_size,
            "size_change": new_size - original_size,
            "lines_written": len(final_content.split('\n')),
            "encoding": encoding,
            "execution_time": round(elapsed_time, 3),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        logger.info(f"Successfully wrote {new_size} bytes to {file_path} in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "mode": mode,
            "content_length": len(content),
            "backup": backup,
            "create_dirs": create_dirs,
            "encoding": encoding
        }
        return enhanced_handle_error("smart_write_file", e, context, agent_name)

@mcp.tool()
def smart_read_file(
    file_path: str,
    encoding: str = "auto",
    max_size: int = 50 * 1024 * 1024,  # 50MB limit
    return_metadata: bool = True
) -> Dict[str, Any]:
    """
    Advanced file reading with encoding detection and metadata.
    
    Args:
        file_path: Path to the file to read
        encoding: Encoding ('auto', 'utf-8', 'latin-1', etc.)
        max_size: Maximum file size to read (bytes)
        return_metadata: Include file metadata in response
        
    Returns:
        File content and metadata or error information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        file_path = Path(file_path).resolve()
        cwd = Path.cwd().resolve()
        
        # Security validation
        if not str(file_path).startswith(str(cwd)):
            error = SecurityError("Access denied: path outside working directory")
            return enhanced_handle_error("smart_read_file", error, 
                                       {"file_path": str(file_path)}, agent_name)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {max_size})")
        
        # Detect encoding if auto
        content = ""
        detected_encoding = encoding
        
        if encoding == "auto":
            # Try common encodings
            for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                    detected_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise UnicodeDecodeError("Could not decode file with any supported encoding")
        else:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            detected_encoding = encoding
        
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "smart_read_file",
            "content": content,
            "agent_name": agent_name
        }
        
        if return_metadata:
            stat = file_path.stat()
            result.update({
                "metadata": {
                    "file_path": str(file_path.relative_to(cwd)),
                    "size": file_size,
                    "lines": len(content.split('\n')),
                    "encoding": detected_encoding,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "execution_time": round(elapsed_time, 3),
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        logger.info(f"Successfully read {file_size} bytes from {file_path} in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "encoding": encoding,
            "max_size": max_size,
            "return_metadata": return_metadata
        }
        return enhanced_handle_error("smart_read_file", e, context, agent_name)

# Add SecurityError class for security violations
class SecurityError(Exception):
    """Custom exception for security violations."""
    pass

@mcp.tool()
def smart_edit_file(
    file_path: str,
    operation: str,
    content: str = "",
    line_number: int = None,
    start_line: int = None,
    end_line: int = None,
    find_text: str = None,
    replace_text: str = None,
    backup: bool = True
) -> Dict[str, Any]:
    """
    Advanced file editing with line-specific operations.
    
    Args:
        file_path: Path to the file to edit
        operation: Edit operation ('insert_at_line', 'replace_line', 'replace_range', 'find_replace', 'delete_line', 'delete_range')
        content: Content to insert/replace (required for insert/replace operations)
        line_number: Line number for single-line operations (1-based)
        start_line: Start line for range operations (1-based)
        end_line: End line for range operations (1-based, inclusive)
        find_text: Text to find for find_replace operation
        replace_text: Replacement text for find_replace operation
        backup: Create backup before editing
        
    Returns:
        Edit result with detailed information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        file_path = Path(file_path).resolve()
        cwd = Path.cwd().resolve()
        
        # Security validation
        if not str(file_path).startswith(str(cwd)):
            error = SecurityError("Access denied: path outside working directory")
            return enhanced_handle_error("smart_edit_file", error, 
                                       {"file_path": str(file_path), "operation": operation}, agent_name)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        original_content = ''.join(original_lines)
        total_lines = len(original_lines)
        
        # Create backup if requested
        backup_path = None
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{int(time.time())}')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Perform the edit operation
        new_lines = original_lines.copy()
        lines_changed = 0
        
        if operation == "insert_at_line":
            if line_number is None:
                raise ValueError("line_number required for insert_at_line operation")
            
            if line_number < 1:
                line_number = 1
            elif line_number > total_lines + 1:
                line_number = total_lines + 1
            
            # Ensure content ends with newline
            if content and not content.endswith('\n'):
                content += '\n'
            
            new_lines.insert(line_number - 1, content)
            lines_changed = 1
            
        elif operation == "replace_line":
            if line_number is None:
                raise ValueError("line_number required for replace_line operation")
            
            if line_number < 1 or line_number > total_lines:
                raise ValueError(f"line_number {line_number} out of range (1-{total_lines})")
            
            # Ensure content ends with newline
            if content and not content.endswith('\n'):
                content += '\n'
            
            new_lines[line_number - 1] = content
            lines_changed = 1
            
        elif operation == "replace_range":
            if start_line is None or end_line is None:
                raise ValueError("start_line and end_line required for replace_range operation")
            
            if start_line < 1 or end_line > total_lines or start_line > end_line:
                raise ValueError(f"Invalid range: {start_line}-{end_line} (file has {total_lines} lines)")
            
            # Ensure content ends with newline if not empty
            if content and not content.endswith('\n'):
                content += '\n'
            
            # Replace the range
            del new_lines[start_line - 1:end_line]
            if content:
                new_lines.insert(start_line - 1, content)
            
            lines_changed = end_line - start_line + 1
            
        elif operation == "find_replace":
            if find_text is None:
                raise ValueError("find_text required for find_replace operation")
            
            if replace_text is None:
                replace_text = ""
            
            for i, line in enumerate(new_lines):
                if find_text in line:
                    new_lines[i] = line.replace(find_text, replace_text)
                    lines_changed += 1
                    
        elif operation == "delete_line":
            if line_number is None:
                raise ValueError("line_number required for delete_line operation")
            
            if line_number < 1 or line_number > total_lines:
                raise ValueError(f"line_number {line_number} out of range (1-{total_lines})")
            
            del new_lines[line_number - 1]
            lines_changed = 1
            
        elif operation == "delete_range":
            if start_line is None or end_line is None:
                raise ValueError("start_line and end_line required for delete_range operation")
            
            if start_line < 1 or end_line > total_lines or start_line > end_line:
                raise ValueError(f"Invalid range: {start_line}-{end_line} (file has {total_lines} lines)")
            
            del new_lines[start_line - 1:end_line]
            lines_changed = end_line - start_line + 1
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Write the modified content
        new_content = ''.join(new_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "smart_edit_file",
            "edit_operation": operation,
            "file_path": str(file_path.relative_to(cwd)),
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path.relative_to(cwd)) if backup_path else None,
            "original_lines": total_lines,
            "new_lines": len(new_lines),
            "lines_changed": lines_changed,
            "original_size": len(original_content.encode('utf-8')),
            "new_size": len(new_content.encode('utf-8')),
            "execution_time": round(elapsed_time, 3),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        logger.info(f"Successfully edited {file_path} ({operation}) in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "operation": operation,
            "line_number": line_number,
            "start_line": start_line,
            "end_line": end_line,
            "find_text": find_text,
            "replace_text": replace_text
        }
        return enhanced_handle_error("smart_edit_file", e, context, agent_name)

@mcp.tool()
def patch_file(
    file_path: str,
    patches: List[Dict[str, Any]],
    backup: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Apply multiple patches to a file in a single operation.
    
    Args:
        file_path: Path to the file to patch
        patches: List of patch operations, each containing:
                 - operation: 'insert', 'replace', 'delete', 'find_replace'
                 - line_number: Line number (for insert/replace/delete)
                 - content: Content to insert/replace (for insert/replace)
                 - find_text: Text to find (for find_replace)
                 - replace_text: Replacement text (for find_replace)
        backup: Create backup before patching
        validate: Validate patch operations before applying
        
    Returns:
        Patch result with detailed information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        file_path = Path(file_path).resolve()
        cwd = Path.cwd().resolve()
        
        # Security validation
        if not str(file_path).startswith(str(cwd)):
            error = SecurityError("Access denied: path outside working directory")
            return enhanced_handle_error("patch_file", error, 
                                       {"file_path": str(file_path)}, agent_name)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        original_content = ''.join(original_lines)
        total_lines = len(original_lines)
        
        # Validate patches if requested
        if validate:
            for i, patch in enumerate(patches):
                if not isinstance(patch, dict):
                    raise ValueError(f"Patch {i} must be a dictionary")
                
                operation = patch.get('operation')
                if not operation:
                    raise ValueError(f"Patch {i} missing 'operation' field")
                
                if operation not in ['insert', 'replace', 'delete', 'find_replace']:
                    raise ValueError(f"Patch {i} has invalid operation: {operation}")
                
                if operation in ['insert', 'replace', 'delete']:
                    if 'line_number' not in patch:
                        raise ValueError(f"Patch {i} missing 'line_number' for {operation} operation")
                    
                    line_num = patch['line_number']
                    if operation == 'insert':
                        if line_num < 1 or line_num > total_lines + 1:
                            raise ValueError(f"Patch {i} line_number {line_num} out of range")
                    else:
                        if line_num < 1 or line_num > total_lines:
                            raise ValueError(f"Patch {i} line_number {line_num} out of range")
                
                if operation in ['insert', 'replace'] and 'content' not in patch:
                    raise ValueError(f"Patch {i} missing 'content' for {operation} operation")
                
                if operation == 'find_replace' and 'find_text' not in patch:
                    raise ValueError(f"Patch {i} missing 'find_text' for find_replace operation")
        
        # Create backup if requested
        backup_path = None
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{int(time.time())}')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Apply patches (sort by line number for insert/replace/delete operations)
        new_lines = original_lines.copy()
        patches_applied = []
        total_changes = 0
        
        # Separate find_replace patches from line-based patches
        line_patches = [p for p in patches if p['operation'] in ['insert', 'replace', 'delete']]
        find_replace_patches = [p for p in patches if p['operation'] == 'find_replace']
        
        # Sort line patches by line number in reverse order to avoid index shifting issues
        line_patches.sort(key=lambda x: x['line_number'], reverse=True)
        
        # Apply find_replace patches first
        for patch in find_replace_patches:
            find_text = patch['find_text']
            replace_text = patch.get('replace_text', '')
            changes_made = 0
            
            for i, line in enumerate(new_lines):
                if find_text in line:
                    new_lines[i] = line.replace(find_text, replace_text)
                    changes_made += 1
            
            patches_applied.append({
                "operation": "find_replace",
                "find_text": find_text,
                "replace_text": replace_text,
                "changes_made": changes_made
            })
            total_changes += changes_made
        
        # Apply line-based patches
        for patch in line_patches:
            operation = patch['operation']
            line_number = patch['line_number']
            
            if operation == 'insert':
                content = patch['content']
                if not content.endswith('\n'):
                    content += '\n'
                new_lines.insert(line_number - 1, content)
                patches_applied.append({
                    "operation": "insert",
                    "line_number": line_number,
                    "content_length": len(content)
                })
                total_changes += 1
                
            elif operation == 'replace':
                content = patch['content']
                if not content.endswith('\n'):
                    content += '\n'
                new_lines[line_number - 1] = content
                patches_applied.append({
                    "operation": "replace",
                    "line_number": line_number,
                    "content_length": len(content)
                })
                total_changes += 1
                
            elif operation == 'delete':
                del new_lines[line_number - 1]
                patches_applied.append({
                    "operation": "delete",
                    "line_number": line_number
                })
                total_changes += 1
        
        # Write the modified content
        new_content = ''.join(new_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        elapsed_time = time.time() - start_time
        
        result = {
            "success": True,
            "operation": "patch_file",
            "file_path": str(file_path.relative_to(cwd)),
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path.relative_to(cwd)) if backup_path else None,
            "patches_requested": len(patches),
            "patches_applied": len(patches_applied),
            "total_changes": total_changes,
            "original_lines": total_lines,
            "new_lines": len(new_lines),
            "original_size": len(original_content.encode('utf-8')),
            "new_size": len(new_content.encode('utf-8')),
            "execution_time": round(elapsed_time, 3),
            "patch_details": patches_applied,
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name
        }
        
        logger.info(f"Successfully patched {file_path} with {len(patches)} patches in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "file_path": str(file_path) if 'file_path' in locals() else file_path,
            "patches": patches,
            "backup": backup,
            "validate": validate
        }
        return enhanced_handle_error("patch_file", e, context, agent_name)

@mcp.tool()
def file_manager(
    operation: str,
    file_path: str = None,
    destination: str = None,
    pattern: str = None,
    confirm: bool = False
) -> Dict[str, Any]:
    """
    Advanced file management operations.
    
    Args:
        operation: File operation ('copy', 'move', 'delete', 'mkdir', 'rmdir', 'backup', 'restore')
        file_path: Source file/directory path
        destination: Destination path (for copy/move operations)
        pattern: Pattern for batch operations
        confirm: Confirmation for destructive operations
        
    Returns:
        Operation result with detailed information
    """
    agent_name = get_agent_name()
    start_time = time.time()
    
    try:
        if operation in ['copy', 'move'] and not destination:
            raise ValueError(f"{operation} operation requires destination parameter")
        
        if operation in ['delete', 'rmdir'] and not confirm:
            return {
                "success": False,
                "message": f"Confirmation required for {operation} operation. Set confirm=True to proceed.",
                "warning": "This action cannot be undone.",
                "operation": operation,
                "file_path": file_path
            }
        
        cwd = Path.cwd().resolve()
        
        if file_path:
            source_path = Path(file_path).resolve()
            # Security validation
            if not str(source_path).startswith(str(cwd)):
                error = SecurityError("Access denied: source path outside working directory")
                return enhanced_handle_error("file_manager", error, 
                                           {"operation": operation, "file_path": file_path}, agent_name)
        
        if destination:
            dest_path = Path(destination).resolve()
            # Security validation
            if not str(dest_path).startswith(str(cwd)):
                error = SecurityError("Access denied: destination path outside working directory")
                return enhanced_handle_error("file_manager", error, 
                                           {"operation": operation, "destination": destination}, agent_name)
        
        result = {
            "success": True,
            "operation": operation,
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if operation == "copy":
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
                result.update({
                    "source": str(source_path.relative_to(cwd)),
                    "destination": str(dest_path.relative_to(cwd)),
                    "size": source_path.stat().st_size,
                    "type": "file"
                })
            elif source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                result.update({
                    "source": str(source_path.relative_to(cwd)),
                    "destination": str(dest_path.relative_to(cwd)),
                    "type": "directory"
                })
            else:
                raise FileNotFoundError(f"Source not found: {source_path}")
                
        elif operation == "move":
            shutil.move(str(source_path), str(dest_path))
            result.update({
                "source": str(source_path.relative_to(cwd)),
                "destination": str(dest_path.relative_to(cwd)),
                "type": "file" if source_path.is_file() else "directory"
            })
            
        elif operation == "delete":
            if source_path.is_file():
                source_path.unlink()
                result.update({
                    "deleted": str(source_path.relative_to(cwd)),
                    "type": "file"
                })
            elif source_path.is_dir():
                shutil.rmtree(source_path)
                result.update({
                    "deleted": str(source_path.relative_to(cwd)),
                    "type": "directory"
                })
            else:
                raise FileNotFoundError(f"Path not found: {source_path}")
                
        elif operation == "mkdir":
            source_path.mkdir(parents=True, exist_ok=True)
            result.update({
                "created": str(source_path.relative_to(cwd)),
                "type": "directory"
            })
            
        elif operation == "backup":
            if not source_path.exists():
                raise FileNotFoundError(f"Source not found: {source_path}")
            
            backup_path = source_path.with_suffix(source_path.suffix + f'.backup.{int(time.time())}')
            
            if source_path.is_file():
                shutil.copy2(source_path, backup_path)
            else:
                shutil.copytree(source_path, backup_path)
            
            result.update({
                "source": str(source_path.relative_to(cwd)),
                "backup": str(backup_path.relative_to(cwd)),
                "type": "file" if source_path.is_file() else "directory"
            })
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        elapsed_time = time.time() - start_time
        result["execution_time"] = round(elapsed_time, 3)
        
        logger.info(f"Successfully completed {operation} operation in {elapsed_time:.3f}s")
        return result
        
    except Exception as e:
        context = {
            "operation": operation,
            "file_path": file_path,
            "destination": destination,
            "pattern": pattern,
            "confirm": confirm
        }
        return enhanced_handle_error("file_manager", e, context, agent_name)

# Add SecurityError class for security violations

# ... existing code ...



# ============================================================================
# CLAUDE INSTANCE MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
def launch_claude_instance(
    role: str = "assistant", 
    project_path: str = None, 
    startup_message: str = None
) -> Dict[str, Any]:
    """
    🚀 Launch a new Claude Code instance with inter-communication capabilities.
    
    Creates a new Claude instance in a separate terminal with its own MCP server,
    enabling multi-agent workflows and collaboration between Claude instances.
    
    Args:
        role: Role for the instance (e.g., "reviewer", "implementer", "coordinator", "tester")
        project_path: Path to project directory (defaults to current working directory)
        startup_message: Initial message to send to the new instance after launch
    
    Returns:
        Dict with launch status, instance ID, and configuration details
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return launch_claude_instance_tool(role, project_path, startup_message)

@mcp.tool()
def list_claude_instances() -> Dict[str, Any]:
    """
    📋 List all active Claude instances with their roles and status.
    
    Shows all currently registered Claude instances, their roles, project paths,
    creation times, and communication endpoints.
    
    Returns:
        Dict with list of instances and summary statistics
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return list_claude_instances_tool()

@mcp.tool()
def send_inter_instance_message(
    target_instance_id: str,
    subject: str, 
    message: str,
    sender_role: str = "coordinator"
) -> Dict[str, Any]:
    """
    💬 Send a message to another Claude instance for coordination.
    
    Enables communication between different Claude instances using the shared
    messaging system. Messages are delivered through the file-based messaging
    infrastructure.
    
    Args:
        target_instance_id: ID of the target Claude instance (from list_claude_instances)
        subject: Message subject line
        message: Message content (can include JSON data, instructions, etc.)
        sender_role: Role of the sender (defaults to "coordinator")
    
    Returns:
        Dict with message delivery status and message ID
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return send_inter_instance_message_tool(target_instance_id, subject, message, sender_role)

@mcp.tool()
def coordinate_claude_instances(
    task: str,
    instance_ids: List[str] = None
) -> Dict[str, Any]:
    """
    🤝 Coordinate multiple Claude instances for a collaborative task.
    
    Sends coordination requests to multiple Claude instances simultaneously,
    enabling complex multi-agent workflows where different instances can
    work on different aspects of a larger task.
    
    Args:
        task: Description of the task to coordinate across instances
        instance_ids: Specific instance IDs to coordinate (if None, coordinates all instances)
    
    Returns:
        Dict with coordination results for each participating instance
    """
    if not CLAUDE_INSTANCES_AVAILABLE:
        return {
            "success": False,
            "error": "Claude instance management tools not available. Check integration setup."
        }
    
    return coordinate_claude_instances_tool(task, instance_ids)

# ============================================================================
# FIREBASE AUTOMATION TOOLS
# ============================================================================

@mcp.tool()
def firebase_setup_new_project(
    project_id: str,
    project_name: str,
    billing_account: str = None,
    region: str = "us-central1",
    web_apps: List[Dict[str, Any]] = None,
    auth_providers: List[Dict[str, Any]] = None,
    services: List[str] = None,
    custom_domains: List[str] = None,
    google_credentials: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    🔥 Create a complete new Firebase project with full automation.
    
    This tool orchestrates the complete Firebase project setup process:
    1. Creates GCP project and enables required APIs
    2. Sets up Firebase Console configuration via web automation
    3. Creates web applications with hosting
    4. Configures authentication providers
    5. Initializes Firebase services (Firestore, Storage, Functions)
    6. Sets up custom domains
    
    Args:
        project_id: Unique project identifier (lowercase, hyphens allowed)
        project_name: Human-readable project name
        billing_account: GCP billing account ID (optional, required for some features)
        region: GCP region for resources (default: us-central1)
        web_apps: List of web applications to create
        auth_providers: Authentication providers to enable
        services: Firebase services to initialize (firestore, storage, functions)
        custom_domains: Custom domains to configure
        google_credentials: Google account credentials for console automation
    
    Returns:
        Dict with project creation results, generated configs, and manual steps
    
    Example:
        firebase_setup_new_project(
            project_id="my-startup-2024",
            project_name="My Startup",
            web_apps=[
                {"name": "Main Website", "setupHosting": True, "hostingSite": "main-site"},
                {"name": "Admin Panel", "setupHosting": True, "hostingSite": "admin"}
            ],
            auth_providers=[
                {"type": "email"},
                {"type": "google"},
                {"type": "github", "clientId": "xxx", "clientSecret": "xxx"}
            ],
            services=["firestore", "storage"],
            google_credentials={"email": "user@gmail.com"}
        )
    """
    try:
        import subprocess
        import json
        import os
        from pathlib import Path
        
        result = {
            "success": False,
            "project_id": project_id,
            "web_apps": [],
            "auth_providers": [],
            "services_configured": [],
            "manual_steps": [],
            "errors": []
        }
        
        # Validate inputs
        if not project_id or not project_name:
            result["errors"].append("project_id and project_name are required")
            return result
        
        # Set defaults
        web_apps = web_apps or []
        auth_providers = auth_providers or []
        services = services or ["firestore", "storage"]
        custom_domains = custom_domains or []
        
        # Step 1: Run GCP infrastructure setup
        try:
            script_path = Path("firebase-setup-automation.sh")
            if not script_path.exists():
                result["errors"].append("firebase-setup-automation.sh not found")
                return result
            
            cmd = [
                "bash", str(script_path),
                project_id, project_name
            ]
            if billing_account:
                cmd.append(billing_account)
                cmd.append(region)
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if process.returncode != 0:
                result["errors"].append(f"GCP setup failed: {process.stderr}")
                return result
                
            result["gcp_setup"] = "completed"
            
        except subprocess.TimeoutExpired:
            result["errors"].append("GCP setup timed out after 5 minutes")
            return result
        except Exception as e:
            result["errors"].append(f"GCP setup error: {str(e)}")
            return result
        
        # Step 2: Run Firebase Console automation
        if google_credentials and web_apps:
            try:
                # Create Node.js automation config
                automation_config = {
                    "projectId": project_id,
                    "webApps": web_apps,
                    "authProviders": auth_providers,
                    "services": services,
                    "customDomains": custom_domains,
                    **google_credentials
                }
                
                config_path = Path("firebase-automation-config.json")
                with open(config_path, "w") as f:
                    json.dump(automation_config, f, indent=2)
                
                # Run Playwright automation
                node_cmd = ["node", "-e", f"""
                const FirebaseAutomator = require('./firebase-console-automation');
                const config = require('./{config_path}');
                
                async function run() {{
                    const automator = new FirebaseAutomator(config.projectId, {{
                        headless: true,
                        authStatePath: './firebase-auth-state.json'
                    }});
                    
                    try {{
                        await automator.init();
                        
                        // Login if needed
                        if (config.email && config.password) {{
                            await automator.login(config.email, config.password);
                        }}
                        
                        // Create web apps
                        for (const app of config.webApps) {{
                            const configText = await automator.createWebApp(app.name, app);
                            console.log(`APP_CONFIG:${{app.name}}:${{configText}}`);
                        }}
                        
                        // Configure authentication
                        if (config.authProviders.length > 0) {{
                            await automator.enableAuthentication(config.authProviders);
                        }}
                        
                        // Configure services
                        for (const service of config.services) {{
                            switch (service) {{
                                case 'firestore':
                                    await automator.configureFirestore();
                                    break;
                                case 'storage':
                                    await automator.configureStorage();
                                    break;
                                case 'functions':
                                    await automator.configureFunctions();
                                    break;
                            }}
                        }}
                        
                        console.log('AUTOMATION_SUCCESS');
                    }} catch (error) {{
                        console.error('AUTOMATION_ERROR:', error.message);
                    }} finally {{
                        await automator.close();
                    }}
                }}
                
                run();
                """]
                
                automation_process = subprocess.run(
                    node_cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=600  # 10 minutes
                )
                
                # Parse automation results
                output_lines = automation_process.stdout.split('\n')
                for line in output_lines:
                    if line.startswith('APP_CONFIG:'):
                        parts = line.split(':', 2)
                        if len(parts) == 3:
                            app_name, config_text = parts[1], parts[2]
                            result["web_apps"].append({
                                "name": app_name,
                                "config": config_text,
                                "status": "created"
                            })
                    elif line.startswith('AUTOMATION_SUCCESS'):
                        result["console_automation"] = "completed"
                    elif line.startswith('AUTOMATION_ERROR:'):
                        result["errors"].append(f"Console automation: {line[18:]}")
                
                # Cleanup
                if config_path.exists():
                    config_path.unlink()
                    
            except subprocess.TimeoutExpired:
                result["errors"].append("Console automation timed out after 10 minutes")
            except Exception as e:
                result["errors"].append(f"Console automation error: {str(e)}")
        
        # Step 3: Collect manual steps
        manual_steps = [
            "Review generated Firebase configuration files",
            "Test authentication providers in Firebase Console"
        ]
        
        # Add OAuth-specific manual steps
        for provider in auth_providers:
            if provider.get("type") == "github":
                manual_steps.append(
                    f"Add callback URL to GitHub OAuth app: "
                    f"https://{project_id}.firebaseapp.com/__/auth/handler"
                )
            elif provider.get("type") == "facebook":
                manual_steps.append(
                    f"Add callback URL to Facebook app: "
                    f"https://{project_id}.firebaseapp.com/__/auth/handler"
                )
        
        # Add domain verification steps
        for domain in custom_domains:
            manual_steps.append(f"Configure DNS records for domain: {domain}")
        
        result["manual_steps"] = manual_steps
        result["success"] = len(result["errors"]) == 0
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Firebase project setup failed: {str(e)}",
            "project_id": project_id
        }

@mcp.tool()
def firebase_configure_existing_project(
    project_id: str,
    google_credentials: Dict[str, str],
    operations: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🔥 Configure an existing Firebase project with additional apps and services.
    
    This tool extends an existing Firebase project by adding new web applications,
    enabling authentication providers, configuring services, and setting up
    custom domains using web automation.
    
    Args:
        project_id: Existing Firebase project ID
        google_credentials: Google account credentials for console access
        operations: Dictionary of operations to perform:
            - createWebApps: List of web apps to create
            - enableAuthProviders: List of auth providers to enable
            - configureServices: List of services to set up
            - addCustomDomains: List of custom domains to add
    
    Returns:
        Dict with configuration results and manual steps required
    
    Example:
        firebase_configure_existing_project(
            project_id="existing-project",
            google_credentials={"email": "user@gmail.com"},
            operations={
                "createWebApps": [
                    {"name": "New Admin Panel", "setupHosting": True}
                ],
                "enableAuthProviders": [
                    {"type": "github", "clientId": "xxx", "clientSecret": "xxx"}
                ],
                "configureServices": ["storage", "functions"],
                "addCustomDomains": ["api.myapp.com"]
            }
        )
    """
    try:
        import subprocess
        import json
        from pathlib import Path
        
        result = {
            "success": False,
            "project_id": project_id,
            "operations_completed": [],
            "operations_failed": [],
            "manual_steps": [],
            "created_apps": []
        }
        
        # Validate inputs
        if not project_id or not google_credentials:
            result["error"] = "project_id and google_credentials are required"
            return result
        
        # Create automation configuration
        automation_config = {
            "projectId": project_id,
            "operations": operations,
            **google_credentials
        }
        
        config_path = Path("firebase-existing-config.json")
        with open(config_path, "w") as f:
            json.dump(automation_config, f, indent=2)
        
        # Run automation script
        node_cmd = ["node", "-e", f"""
        const FirebaseAutomator = require('./firebase-console-automation');
        const config = require('./{config_path}');
        
        async function run() {{
            const automator = new FirebaseAutomator(config.projectId, {{
                headless: true,
                authStatePath: './firebase-auth-state.json'
            }});
            
            try {{
                await automator.init();
                
                // Login if needed
                if (config.email && config.password) {{
                    await automator.login(config.email, config.password);
                }}
                
                const ops = config.operations;
                
                // Create web apps
                if (ops.createWebApps) {{
                    for (const app of ops.createWebApps) {{
                        try {{
                            const configText = await automator.createWebApp(app.name, app);
                            console.log(`CREATED_APP:${{app.name}}:success`);
                        }} catch (error) {{
                            console.log(`CREATED_APP:${{app.name}}:failed:${{error.message}}`);
                        }}
                    }}
                }}
                
                // Enable auth providers
                if (ops.enableAuthProviders) {{
                    try {{
                        await automator.enableAuthentication(ops.enableAuthProviders);
                        console.log('AUTH_PROVIDERS:success');
                    }} catch (error) {{
                        console.log(`AUTH_PROVIDERS:failed:${{error.message}}`);
                    }}
                }}
                
                // Configure services
                if (ops.configureServices) {{
                    for (const service of ops.configureServices) {{
                        try {{
                            switch (service) {{
                                case 'firestore':
                                    await automator.configureFirestore();
                                    break;
                                case 'storage':
                                    await automator.configureStorage();
                                    break;
                                case 'functions':
                                    await automator.configureFunctions();
                                    break;
                            }}
                            console.log(`SERVICE:${{service}}:success`);
                        }} catch (error) {{
                            console.log(`SERVICE:${{service}}:failed:${{error.message}}`);
                        }}
                    }}
                }}
                
                // Add custom domains
                if (ops.addCustomDomains) {{
                    for (const domain of ops.addCustomDomains) {{
                        try {{
                            await automator.configureHosting(domain);
                            console.log(`DOMAIN:${{domain}}:success`);
                        }} catch (error) {{
                            console.log(`DOMAIN:${{domain}}:failed:${{error.message}}`);
                        }}
                    }}
                }}
                
                console.log('AUTOMATION_COMPLETE');
                
            }} catch (error) {{
                console.error('AUTOMATION_ERROR:', error.message);
            }} finally {{
                await automator.close();
            }}
        }}
        
        run();
        """]
        
        automation_process = subprocess.run(
            node_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        # Parse results
        output_lines = automation_process.stdout.split('\n')
        for line in output_lines:
            if line.startswith('CREATED_APP:'):
                parts = line.split(':', 3)
                if len(parts) >= 3:
                    app_name, status = parts[1], parts[2]
                    if status == "success":
                        result["operations_completed"].append(f"Created app: {app_name}")
                        result["created_apps"].append(app_name)
                    else:
                        error_msg = parts[3] if len(parts) > 3 else "Unknown error"
                        result["operations_failed"].append(f"Failed to create app {app_name}: {error_msg}")
            
            elif line.startswith('AUTH_PROVIDERS:'):
                status = line.split(':', 1)[1]
                if status == "success":
                    result["operations_completed"].append("Configured authentication providers")
                else:
                    result["operations_failed"].append(f"Auth providers failed: {status}")
            
            elif line.startswith('SERVICE:'):
                parts = line.split(':', 2)
                service, status = parts[1], parts[2]
                if status.startswith("success"):
                    result["operations_completed"].append(f"Configured service: {service}")
                else:
                    error_msg = status.replace("failed:", "")
                    result["operations_failed"].append(f"Service {service} failed: {error_msg}")
            
            elif line.startswith('DOMAIN:'):
                parts = line.split(':', 2)
                domain, status = parts[1], parts[2]
                if status.startswith("success"):
                    result["operations_completed"].append(f"Configured domain: {domain}")
                    result["manual_steps"].append(f"Complete DNS verification for: {domain}")
                else:
                    error_msg = status.replace("failed:", "")
                    result["operations_failed"].append(f"Domain {domain} failed: {error_msg}")
        
        # Cleanup
        if config_path.exists():
            config_path.unlink()
        
        result["success"] = len(result["operations_failed"]) == 0
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Firebase configuration failed: {str(e)}",
            "project_id": project_id
        }

@mcp.tool()
def firebase_project_status(project_id: str) -> Dict[str, Any]:
    """
    🔥 Get the current configuration status of a Firebase project.
    
    This tool queries the Firebase project to determine the current state
    of web applications, authentication providers, services, and domains.
    Uses Firebase CLI and web automation to gather comprehensive status.
    
    Args:
        project_id: Firebase project ID to check
    
    Returns:
        Dict with detailed project status information
    
    Example:
        firebase_project_status("my-project-2024")
    """
    try:
        import subprocess
        import json
        from pathlib import Path
        
        result = {
            "success": False,
            "project_id": project_id,
            "web_apps": [],
            "auth_providers": [],
            "services": {},
            "custom_domains": [],
            "billing_status": "unknown"
        }
        
        # Check if Firebase CLI is available and project exists
        try:
            # Get project info using Firebase CLI
            cli_result = subprocess.run(
                ["firebase", "projects:list", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if cli_result.returncode == 0:
                projects = json.loads(cli_result.stdout)
                project_found = any(p.get("projectId") == project_id for p in projects)
                
                if not project_found:
                    result["error"] = f"Project {project_id} not found or not accessible"
                    return result
                
                result["project_exists"] = True
            else:
                result["error"] = "Firebase CLI not available or not authenticated"
                return result
                
        except subprocess.TimeoutExpired:
            result["error"] = "Firebase CLI command timed out"
            return result
        except json.JSONDecodeError:
            result["error"] = "Failed to parse Firebase CLI output"
            return result
        
        # Get web apps list
        try:
            apps_result = subprocess.run(
                ["firebase", "apps:list", "--project", project_id, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if apps_result.returncode == 0:
                apps_data = json.loads(apps_result.stdout)
                for app in apps_data:
                    if app.get("platform") == "WEB":
                        result["web_apps"].append({
                            "name": app.get("displayName", "Unknown"),
                            "app_id": app.get("appId"),
                            "status": "active"
                        })
                        
        except Exception as e:
            result["web_apps_error"] = str(e)
        
        # Check Firebase services using GCP CLI
        try:
            services_result = subprocess.run(
                ["gcloud", "services", "list", "--enabled", "--project", project_id, "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if services_result.returncode == 0:
                services = json.loads(services_result.stdout)
                service_names = [s.get("config", {}).get("name", "") for s in services]
                
                result["services"] = {
                    "firestore": "firestore.googleapis.com" in service_names,
                    "storage": "firebasestorage.googleapis.com" in service_names,
                    "functions": "cloudfunctions.googleapis.com" in service_names,
                    "hosting": "firebasehosting.googleapis.com" in service_names,
                    "auth": "firebase.googleapis.com" in service_names
                }
                
        except Exception as e:
            result["services_error"] = str(e)
        
        # Check billing status
        try:
            billing_result = subprocess.run(
                ["gcloud", "billing", "projects", "describe", project_id, "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if billing_result.returncode == 0:
                billing_data = json.loads(billing_result.stdout)
                result["billing_status"] = "enabled" if billing_data.get("billingEnabled") else "disabled"
                result["billing_account"] = billing_data.get("billingAccountName", "")
            else:
                result["billing_status"] = "unknown"
                
        except Exception as e:
            result["billing_error"] = str(e)
        
        result["success"] = True
        result["last_checked"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Status check failed: {str(e)}",
            "project_id": project_id
        }

@mcp.tool()
def firebase_batch_operations(
    project_id: str,
    operations: List[Dict[str, Any]],
    options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    🔥 Perform multiple Firebase operations in sequence with error handling.
    
    This tool executes a batch of Firebase operations in the specified order,
    with options for error handling, delays between operations, and rollback
    capabilities.
    
    Args:
        project_id: Firebase project ID
        operations: List of operations to perform, each with type and config
        options: Batch execution options (continueOnError, delayBetweenOperations, etc.)
    
    Returns:
        Dict with results of each operation and overall batch status
    
    Example:
        firebase_batch_operations(
            project_id="my-project",
            operations=[
                {"type": "create_web_app", "config": {"name": "App 1", "setupHosting": True}},
                {"type": "create_web_app", "config": {"name": "App 2", "setupHosting": True}},
                {"type": "enable_auth_provider", "config": {"type": "email"}},
                {"type": "configure_service", "config": {"service": "firestore"}}
            ],
            options={"continueOnError": False, "delayBetweenOperations": 2000}
        )
    """
    try:
        import time
        from typing import List, Dict, Any
        
        # Set default options
        options = options or {}
        continue_on_error = options.get("continueOnError", False)
        delay_ms = options.get("delayBetweenOperations", 1000)
        
        result = {
            "success": False,
            "project_id": project_id,
            "operations_requested": len(operations),
            "operations_completed": 0,
            "operations_failed": 0,
            "results": [],
            "errors": []
        }
        
        # Validate inputs
        if not operations:
            result["error"] = "No operations specified"
            return result
        
        for i, operation in enumerate(operations):
            operation_result = {
                "index": i,
                "type": operation.get("type"),
                "config": operation.get("config", {}),
                "success": False,
                "error": None,
                "duration_ms": 0
            }
            
            try:
                start_time = time.time()
                
                # Execute operation based on type
                op_type = operation.get("type")
                op_config = operation.get("config", {})
                
                if op_type == "create_web_app":
                    # Create web app operation
                    app_result = firebase_configure_existing_project(
                        project_id=project_id,
                        google_credentials=options.get("googleCredentials", {}),
                        operations={"createWebApps": [op_config]}
                    )
                    operation_result["success"] = app_result.get("success", False)
                    if not operation_result["success"]:
                        operation_result["error"] = app_result.get("error", "Unknown error")
                
                elif op_type == "enable_auth_provider":
                    # Enable authentication provider
                    auth_result = firebase_configure_existing_project(
                        project_id=project_id,
                        google_credentials=options.get("googleCredentials", {}),
                        operations={"enableAuthProviders": [op_config]}
                    )
                    operation_result["success"] = auth_result.get("success", False)
                    if not operation_result["success"]:
                        operation_result["error"] = auth_result.get("error", "Unknown error")
                
                elif op_type == "configure_service":
                    # Configure Firebase service
                    service_result = firebase_configure_existing_project(
                        project_id=project_id,
                        google_credentials=options.get("googleCredentials", {}),
                        operations={"configureServices": [op_config.get("service")]}
                    )
                    operation_result["success"] = service_result.get("success", False)
                    if not operation_result["success"]:
                        operation_result["error"] = service_result.get("error", "Unknown error")
                
                else:
                    operation_result["error"] = f"Unknown operation type: {op_type}"
                
                # Calculate duration
                operation_result["duration_ms"] = int((time.time() - start_time) * 1000)
                
                if operation_result["success"]:
                    result["operations_completed"] += 1
                else:
                    result["operations_failed"] += 1
                    result["errors"].append(f"Operation {i}: {operation_result['error']}")
                    
                    # Stop on error if not continuing
                    if not continue_on_error:
                        break
                
            except Exception as e:
                operation_result["error"] = str(e)
                operation_result["duration_ms"] = int((time.time() - start_time) * 1000)
                result["operations_failed"] += 1
                result["errors"].append(f"Operation {i} exception: {str(e)}")
                
                if not continue_on_error:
                    break
            
            result["results"].append(operation_result)
            
            # Delay between operations
            if i < len(operations) - 1 and delay_ms > 0:
                time.sleep(delay_ms / 1000.0)
        
        result["success"] = result["operations_failed"] == 0
        result["completion_rate"] = result["operations_completed"] / result["operations_requested"]
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Batch operations failed: {str(e)}",
            "project_id": project_id
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidated MCP Server v2.0")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Server port")
    parser.add_argument("--host", default=SERVER_HOST, help="Server host")
    parser.add_argument("--stdio", action="store_true", help="Use STDIO transport")
    
    args = parser.parse_args()
    if not args.stdio:
        print(f"""
    🚀 Consolidated MCP Server v{SERVER_VERSION} Starting
    ==============================================
    ✅ Enhanced Security: Path validation and input sanitization
    ✅ Robust Error Handling: Comprehensive exception management
    ✅ Chrome Debug Integration: Real-time monitoring and execution
    ✅ Resource Management: Automatic cleanup and connection tracking
    ✅ Unicode Safety: Emoji and special character support
    ✅ Thread Safety: Protected shared resources
    """)
    
    if args.stdio:
        # Don't print anything to stdout in STDIO mode - it breaks Claude Desktop
        logger.info("Starting Consolidated MCP Server in STDIO mode")
        mcp.run(transport="stdio")
    else:
        print(f"🎯 Starting HTTP transport on {args.host}:{args.port}")
        logger.info(f"Starting Consolidated MCP Server v{SERVER_VERSION} on {args.host}:{args.port}")
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
