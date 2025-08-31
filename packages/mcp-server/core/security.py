"""
Security utilities for MCP server.

This module provides security-related functions and exceptions for path validation
and access control.
"""

from pathlib import Path
from typing import Union


class SecurityError(Exception):
    """Custom exception for security violations."""
    pass


def validate_path_security(file_path: Union[str, Path], base_path: Union[str, Path] = None) -> Path:
    """
    Validate that a file path is within the allowed base directory.
    
    Args:
        file_path: Path to validate
        base_path: Base directory to validate against (defaults to current working directory)
        
    Returns:
        Resolved Path object if valid
        
    Raises:
        SecurityError: If path is outside the base directory
    """
    if base_path is None:
        base_path = Path.cwd()
    
    file_path = Path(file_path).resolve()
    base_path = Path(base_path).resolve()
    
    if not str(file_path).startswith(str(base_path)):
        raise SecurityError(f"Access denied: path '{file_path}' is outside base directory '{base_path}'")
    
    return file_path


def is_path_safe(file_path: Union[str, Path], base_path: Union[str, Path] = None) -> bool:
    """
    Check if a file path is within the allowed base directory.
    
    Args:
        file_path: Path to check
        base_path: Base directory to check against (defaults to current working directory)
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        validate_path_security(file_path, base_path)
        return True
    except SecurityError:
        return False