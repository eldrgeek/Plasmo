#!/usr/bin/env python3
"""
Files Module - Advanced File Operations for MCP Server
======================================================

This module provides comprehensive file operations with enhanced security,
error handling, and metadata tracking specifically designed for AI assistants.

Submodules:
- smart_operations: Advanced read/write/edit operations with encoding detection
- file_manager: File system operations (copy, move, delete, backup)

All operations include:
- Security validation (path traversal protection)
- Comprehensive error handling with agent tracking
- Backup management for destructive operations
- Detailed metadata and performance reporting
- UTF-8 and international character support
"""

from .smart_operations import (
    smart_write_file,
    smart_read_file,
    smart_edit_file,
    patch_file,
    set_working_directory
)

from .file_manager import (
    file_manager
)

__all__ = [
    # Smart file operations
    "smart_write_file",
    "smart_read_file", 
    "smart_edit_file",
    "patch_file",
    "set_working_directory",
    
    # File management operations
    "file_manager"
]

# Version information
__version__ = "1.0.0"
__author__ = "MCP Server Development Team"
__description__ = "Advanced file operations module for MCP server"