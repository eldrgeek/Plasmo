"""
Core utilities for MCP server.

This package provides modular components for the MCP server including:
- JSON utilities for safe serialization
- Security utilities for path validation
- Error handling with agent tracking
- Server state management
"""

# Import main components for easy access
from .json_utils import make_json_safe
from .security import SecurityError, validate_path_security, is_path_safe
from .error_handling import (
    enhanced_handle_error, 
    handle_error, 
    log_agent_error,
    get_error_suggestion,
    get_last_errors,
    clear_agent_errors,
    set_custom_agent_name,
    get_agent_name
)
from .server_state import ServerState, server_state, run_background_task, get_server_state

__all__ = [
    # JSON utilities
    'make_json_safe',
    
    # Security utilities
    'SecurityError',
    'validate_path_security',
    'is_path_safe',
    
    # Error handling
    'enhanced_handle_error',
    'handle_error',
    'log_agent_error',
    'get_error_suggestion',
    'get_last_errors',
    'clear_agent_errors',
    'set_custom_agent_name',
    'get_agent_name',
    
    # Server state
    'ServerState',
    'server_state',
    'run_background_task',
    'get_server_state'
]