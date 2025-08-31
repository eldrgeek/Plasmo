"""
Error handling utilities for MCP server.

This module provides enhanced error handling with agent tracking and detailed logging.
"""

import logging
import threading
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .json_utils import make_json_safe

logger = logging.getLogger(__name__)

# Global error tracking
agent_error_logs: Dict[str, list] = {}  # agent_name -> list of error entries
error_log_lock = threading.Lock()

# Agent name tracking
_custom_agent_name: Optional[str] = None


def set_custom_agent_name(name: str) -> None:
    """Set a custom agent name for error tracking."""
    global _custom_agent_name
    _custom_agent_name = name


def get_custom_agent_name() -> str:
    """Get agent name - custom name if set, otherwise current repo directory."""
    global _custom_agent_name
    if _custom_agent_name:
        return _custom_agent_name
    return Path.cwd().name


def get_agent_name() -> str:
    """Get agent name - custom name if set, otherwise current repo directory."""
    return get_custom_agent_name()


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


def clear_agent_errors(agent_name: str = None) -> Dict[str, Any]:
    """
    Clear error logs for an agent.
    
    Args:
        agent_name: Agent name (defaults to current agent)
        
    Returns:
        Dictionary with operation result
    """
    try:
        if agent_name is None:
            agent_name = get_agent_name()
        
        with error_log_lock:
            errors_cleared = len(agent_error_logs.get(agent_name, []))
            agent_error_logs[agent_name] = []
        
        return {
            "success": True,
            "agent_name": agent_name,
            "errors_cleared": errors_cleared,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return handle_error("clear_agent_errors", e)